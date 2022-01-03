import json
import csv
import mimetypes
import os
from django.conf import settings
from operator import itemgetter
import itertools
from functools import reduce
from datetime import datetime, date, timedelta
from django.http import Http404, HttpResponse, StreamingHttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum,Q
from django.db.models.functions import ExtractMonth, ExtractYear
from django.forms.models import model_to_dict
from suiviprojets.dashboard.models import TypePrestation,CategorieForfait,Flux,Forfait,TypeEchange,Echange,Contact \
                                            ,StatutTache, Tache,Consommation,Prestation,Client
from wsgiref.util import FileWrapper



# Create your views here.
MOIS=[{'tag':'janvier','days':31},{'tag':'février','days':29},{'tag':'mars','days':31}, \
		{'tag':'avril','days':30},{'tag':'mai','days':31},{'tag':'juin','days':30}, \
		{'tag':'juillet','days':31},{'tag':'août','days':31},{'tag':'septembre','days':30}, \
		{'tag':'octobre','days':31},{'tag':'novembre','days':30},{'tag':'décembre','days':31}]
		
BASE_FIELDS={'id':'id',
			'sport':'sport_type',
			'date':'date',
			'distance':'distance',
			'duree':'duree',
			}
			
SEARCH_TERMS={'id':'id',
			'date_debut':'date__gt',
			'date_fin':'date__lt',
			'sport_type':'sport_type__in',
			}
			
SCRIPTS=['common','dashboard','node_modules/fullcalendar/main.min','index']
STYLES=['js/node_modules/chart.js/dist/Chart.min.css',
		'js/node_modules/fullcalendar/main.min.css','scss/styles.css']


def client_compose_index(c):
	client=model_to_dict(c)
	forfait=Forfait.objects.filter(client=c.id).last()
	taches=Tache.objects.filter(client=c.id,statut__statut='en cours')
	echanges=Echange.objects.filter(contact__client_id=c.id,date__gt=date.today()).order_by('-date')
	prestations=Prestation.objects.filter(client=c.id,statut__statut__in=['en attente','en cours'])
	client['taches']=[t.nom for t in taches]
	client['forfait']=forfait
	client['echanges']=[str(e.date)+":"+str(e.contact.nom) for e in echanges]
	client['prestations']=[str(p.type_prestation)+":"+str(p.statut.statut) for p in prestations]
	return client

def __add_statut(value,color_statut):
	flag="<span class=\'statut\' style=\'background-color:#"+color_statut+";\'></span>"
	value="<span class=\'value\'>"+value+"</span>"
	return "<p>"+str(" ".join([flag,value]))+"</p>"
	
	
def client_compose_details(id):
	instance_client=Client.objects.get(pk=id)
	client=model_to_dict(instance_client)
	forfait=Forfait.objects.filter(client=id).last
	taches=Tache.objects.filter(client_id=id)
	echanges=Echange.objects.filter(contact__client_id=id).order_by('-date')
	prestations=Prestation.objects.filter(client=id)
	
	contacts=Contact.objects.filter(client=id).order_by("nom")
	
	client['taches']=taches
	client['contacts']=contacts
	client['forfait']=forfait
	client['echanges']=echanges
	client['prestations']= prestations
	""" parsage des evenements """
	""" un evenement se compose 
		-title
		-start
		-end
		l'ensemble des events peut avoir les propriétés
		color
		background-color"""
	
	tasks=Tache.objects.filter(client_id=id,statut__statut__in=["à programmer","en attente","en cours"])
	tasks_events={'events':[{'title':t.nom,'start':str(t.date_programmee),'statut':t.statut.color} for t in tasks],'color':'green','textColor':'white'}
	
	prestations=Prestation.objects.filter(statut__statut__in=["en attente","à programmer","en cours"])
	prestations_events={'events':[{'title':p.type_prestation.type_prestation,'start':str(p.date_programmee),'statut':p.statut.color} for p in prestations],'color':'green','textColor':'white'}

	echanges=Echange.objects.filter(contact__client_id=id,statut__statut__in=["en attente","à programmer","en cours"])
	echanges_events={'events':[{'title':e.type_echange.type_echange,'statut':e.statut.color,'start':str(e.date)} for e in echanges],'color':'light-green','textColor': 'white'}
	
	client['eventsct']=json.dumps(tasks_events)
	client['eventscp']=json.dumps(prestations_events)
	client['eventsce']=json.dumps(echanges_events)
	
	return client
	
"""/*************************
   * View dashboard
   * procedure
   * @brief fonction gerant l'affichage des deux tableaux
	 et 3 graphiques du tableau de bord
	 @position définie comme page d'accueil
	 @authentification oui
	 @role             utilisateur
   *************************/"""
def index(request):
	
	"""if request.session.get('filtres') == None:
		request.session['sort']={'field':'date','sens':'desc'}
		request.session['nb_items']=10
		request.session['filtres']=[{}]
		request.session['message']=""
		request.session['actions']=[]"""
	
	toprogram_prestations=Prestation.objects.filter(Q(statut__statut__in=["en attente","à programmer"])|Q(date_programmee__isnull=True)).values('client__nom','type_prestation__type_prestation','id')
	toprogram_tasks=Tache.objects.filter(Q(statut__statut__in=["en attente","à programmer"]) | Q(date_programmee__isnull=True)).values('client__nom','nom','id')
	next_echanges=Echange.objects.filter(statut__statut__in=["en attente","à programmer"]).values('contact__nom','contact__prenom','date','heure','type_echange__type_echange','id')
	clients=Client.objects.all()
	Dclients=[client_compose_index(c) for c in clients]

	datas={'partial':'dashboard/index.html',
			'toprogram_prestations':toprogram_prestations,
			'toprogram_tasks':toprogram_tasks,
			'next_echanges':next_echanges,
			'scripts':SCRIPTS,
			'styles':STYLES,}

	return render(request,"index.html",datas)
	
def projets(request):
	clients=Client.objects.all()
	Dclients=[client_compose_index(c) for c in clients]
	datas={'partial':'dashboard/liste.html',
			'liste':Dclients,
			'scripts':SCRIPTS,
			'styles':STYLES,}
	return render(request,"index.html",datas)
	
def details(request,id):
	client=client_compose_details(id)
	datas={'partial':'dashboard/details.html',
			'client':client,
			'styles':STYLES,
			'scripts':SCRIPTS,}
	return render(request,"index.html",datas)
	
def currents(request):
	events_tasks = [{"id":t.id,"resourceId":t.client.id,"resourceTitle":t.client.nom,"title":t.nom,"color":"green","start":str(t.date_programmee),"end":str(t.date_realisation)} for t in Tache.objects.filter(statut__statut__in=['en attente','en cours'],date_programmee__isnull=False)]
	events_prestations = [{"id":p.id,"resourceId":p.client.id,"title":str(p.type_prestation),"color":"pink","start":str(p.date_programmee),"end":str(p.date_realisation)} for p in Prestation.objects.filter(statut__statut__in=['en attente','en cours'],date_programmee__isnull=False)]
	events=events_tasks+events_prestations
	tab_check_client=[]
	resources=[]
	i=0
	for e in events:
		if e['resourceId'] not in tab_check_client:
			tab_check_client.append(e['resourceId'])
			resources.append({"id":e['resourceId'],"title":e['resourceTitle'],"rowColor":(i%2==0) and "blue" or "white"})
			i+=1
	datas={'partial':'dashboard/current_tasks.html',
			'scripts':SCRIPTS+['node_modules/fullcalendar-scheduler/main'],
			'styles':STYLES+['js/node_modules/fullcalendar-scheduler/main.css'],
			'resources':json.dumps(resources),
			'events':json.dumps(events),
			}
	return render(request,"index.html",datas)

def download(request):

    """filtre=request.session['filtres']
    sessions=Session.objects.all()
    filtered_items=apply_filter(sessions,filtre)
    items=filtered_items.order_by('date','sport_type')
    lines=__parse_items(items)"""
    forfaits=Forfait.objects.all()
    lines=[]
    i=0
    for f in Forfait.objects.all().order_by('id'):
        i+=1

        lines.append({'nom':f.client.nom,'date':f.date_commande,'num_armoire':f.client.num_armoire,'adresse1':f.client.adresse1,'adresse2':f.client.adresse2,'code_postal':f.client.code_postal,\
        'ville':f.client.ville,'revendeur':f.client.revendeur.nom,'forfait':f.categorie_forfait})
    
    
    """lines=[{'nom':f.client.nom,'date':f.date_commande,'num_armoire':f.client.num_armoire,'adresse1':f.client.adresse1,'adresse2':f.client.adresse2,'code_postal':f.client.code_postal,\
    'ville':f.client.ville,'revendeur':f.client.revendeur.nom,'forfait':f.categorie_forfait} for f in Forfait.objects.all().order_by('client__num_armoire')]"""
    
    labels=['nom','date','num_armoire','adresse1','adresse2','code_postal','ville','revendeur','forfait']

    tempfile="/".join([settings.TMP_ROOT,"datastmp.csv"])

    with open(tempfile,"a") as fich:
        writer=csv.DictWriter(fich,fieldnames=labels,delimiter=";",dialect='excel')
        writer.writeheader()
        for line in lines:
            writer.writerow(line)
        fich.close()

    filec=open(tempfile,"r")

    response=HttpResponse(FileWrapper(filec),content_type=mimetypes.guess_type(filec.name)[0])
    response['Content-Disposition']='attachment; filename='+filec.name
    os.remove(tempfile)

    return response
