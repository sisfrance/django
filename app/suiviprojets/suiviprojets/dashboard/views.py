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
from suiviprojets.dashboard.models import Projet,TypeProjet,TypePrestation,CategorieForfait,Flux,Forfait,TypeEchange,Echange,Contact \
                                            ,StatutTache, Tache,Consommation,Prestation,Client
from suiviprojets.dashboard.forms import ContactForm
from suiviprojets.helpers.helpers import apply_filter, filter_construct, Pager
from wsgiref.util import FileWrapper



# Create your views here.
MOIS=[{'tag':'janvier','days':31},{'tag':'février','days':29},{'tag':'mars','days':31}, \
		{'tag':'avril','days':30},{'tag':'mai','days':31},{'tag':'juin','days':30}, \
		{'tag':'juillet','days':31},{'tag':'août','days':31},{'tag':'septembre','days':30}, \
		{'tag':'octobre','days':31},{'tag':'novembre','days':30},{'tag':'décembre','days':31}]
		
BASE_FIELDS={'id':'id',
			'num_armoire':'num_armoire',
			'type_projet':'type_projet',
			'client':'client',
			}
			
SEARCH_TERMS={'num_armoire':'num_armoire__icontains',
			'nom':'client__nom__icontains',
			'forfait':'forfait_id',
			}
			
SCRIPTS=['common','node_modules/fullcalendar/main.min','index']
STYLES=['js/node_modules/chart.js/dist/Chart.min.css',
		'js/node_modules/fullcalendar/main.min.css','scss/styles.css']


def projet_compose_liste(p):
	client=p.client
	projet={"id":p.id,
			"client":{'nom':p.client.nom,'id':p.client.id},
			"type_projet":str(p.type_projet),
			"num_armoire":p.num_armoire,
			}
	forfait=Forfait.objects.filter(projet=p.id).last()
	taches=Tache.objects.filter(projet=p.id,statut__statut='en cours')
	echanges=Echange.objects.filter(contact__client_id=client.id,date__gt=date.today()).order_by('-date')
	prestations=Prestation.objects.filter(projet=p.id,statut__statut__in=['en attente','en cours'])
	projet['taches']=[t.nom for t in taches]
	projet['debut_forfait']=str(forfait.date_commande)
	projet['categorie_forfait']=forfait.categorie_forfait.categorie_forfait
	projet['echanges']=[str(e.date)+":"+str(e.contact.nom) for e in echanges]
	projet['prestations']=[str(pres.type_prestation)+":"+str(pres.statut.statut) for pres in prestations]
	return projet


def projet_compose_details(id):
	instance_projet=Projet.objects.get(pk=id)
	projet={"id":instance_projet.id,
			"client":instance_projet.client.nom,
			"type_projet":str(instance_projet.type_projet),
			"num_armoire":instance_projet.num_armoire
			}

	client=instance_projet.client
	forfait=Forfait.objects.filter(projet=id).last
	taches=Tache.objects.filter(projet_id=id)
	echanges=Echange.objects.filter(contact__client_id=client.id).order_by('-date')
	prestations=Prestation.objects.filter(projet=id)
	contacts=Contact.objects.filter(client=instance_projet.client.id,type_projet=instance_projet.type_projet.id).order_by("nom")
	
	projet['taches']=taches
	projet['contacts']=contacts
	projet['forfait']=forfait
	projet['echanges']=echanges
	projet['prestations']= prestations
	
	""" parsage des evenements """
	""" un evenement se compose 
		-title
		-start
		-end
		l'ensemble des events peut avoir les propriétés
		color
		background-color"""
	
	tasks=Tache.objects.filter(projet_id=id,statut__statut__in=["à programmer","en attente","en cours"])
	tasks_events={'events':[{'title':t.nom,'start':str(t.date_programmee),'statut':t.statut.color,'description':t.description} for t in tasks],'color':'green','textColor':'white'}
	
	prestations=Prestation.objects.filter(projet_id=id,statut__statut__in=["en attente","à programmer","en cours"])
	prestations_events={'events':[{'title':p.type_prestation.type_prestation,'start':str(p.date_programmee),'statut':p.statut.color,'description':p.notes} for p in prestations],'color':'green','textColor':'white'}

	echanges=Echange.objects.filter(contact__client_id=client.id,statut__statut__in=["en attente","à programmer","en cours"])
	echanges_events={'events':[{'title':e.type_echange.type_echange,'statut':e.statut.color,'start':str(e.date),'description':e.notes} for e in echanges],'color':'light-green','textColor': 'white'}
	
	projet['eventsct']=json.dumps(tasks_events)
	projet['eventscp']=json.dumps(prestations_events)
	projet['eventsce']=json.dumps(echanges_events)

	return projet
	
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
	
	toprogram_prestations=Prestation.objects.filter(Q(statut__statut__in=["en attente","à programmer"])|Q(date_programmee__isnull=True)).values('projet__client__nom','type_prestation__type_prestation','id')
	toprogram_tasks=Tache.objects.filter(Q(statut__statut__in=["en attente","à programmer"]) | Q(date_programmee__isnull=True)).values('projet__client__nom','nom','id')
	next_echanges=Echange.objects.filter(statut__statut__in=["en attente","à programmer"]).values('contact__nom','contact__prenom','date','heure','type_echange__type_echange','id')

	datas={'partial':'dashboard/index.html',
			'toprogram_prestations':toprogram_prestations,
			'toprogram_tasks':toprogram_tasks,
			'next_echanges':next_echanges,
			'scripts':SCRIPTS,
			'styles':STYLES,}

	return render(request,"index.html",datas)
	
def projets(request):
	
	"""if request.session.get('filtres') === None:"""
	request.session['sort']={'field':'num_armoire','sens':'desc'}
	request.session['nb_items']=10
	request.session['filtres']=[{}]
	request.session['message']=""
	request.session['actions']=[]

			
	projets=Projet.objects.all()
	pagination=Pager(projets,"projects").paginate()
	
	Dprojets=[projet_compose_liste(p) for p in pagination[0]]

	datas={'partial':'dashboard/liste.html',
			'liste':Dprojets,
			'total_elts':pagination[2],
			'pagination':pagination[1],
			'scripts':SCRIPTS,
			'styles':STYLES,}
	return render(request,"index.html",datas)
	
def details(request,id):
	projet=projet_compose_details(id)
	datas={'partial':'dashboard/details.html',
			'projet':projet,
			'styles':STYLES,
			'scripts':SCRIPTS,}
	return render(request,"index.html",datas)
	
def details_client(request,id):
	client=Client.objects.get(pk=id)
	contacts=Contact.objects.filter(client=id).order_by('nom')

	datas={'partial':'dashboard/details_client.html',
			'client':client,
			'contacts':contacts,
			'scripts':SCRIPTS+['node_modules/fullcalendar-scheduler/main'],
			'styles':STYLES+['js/node_modules/fullcalendar-scheduler/main.css'],
			'resources':json.dumps([]),
			'events':json.dumps([]),
			}
	return render(request,"index.html",datas)
	
def clients(request):
	pass
	
def currents(request):
	events_tasks = [{"id":t.id,"resourceId":t.client.id,"resourceTitle":t.client.nom,"title":t.nom,"color":"green","start":str(t.date_programmee),"end":str(t.date_realisation),"statut":t.statut.color,"description":t.description} for t in Tache.objects.filter(statut__statut__in=['en attente','en cours'],date_programmee__isnull=False)]
	events_prestations = [{"id":p.id,"resourceId":p.client.id,"resourceTitle":p.client.nom,"title":str(p.type_prestation),"color":"pink","start":str(p.date_programmee),"end":str(p.date_realisation),"statut":p.statut.color,"description":p.notes} for p in Prestation.objects.filter(statut__statut__in=['en attente','en cours'],date_programmee__isnull=False)]
	events_echanges = [{"id":e.id,"resourceId":e.contact.client.id,"resourceTitle":e.contact.client.nom,"title":str(e.type_echange),"color":"blue","start":str(e.date),"end":None,"statut":e.statut.color,"description":e.notes} for e in Echange.objects.filter(statut__statut__in=['en attente','en cours'],date__isnull=False)]
	events=events_tasks+events_prestations+events_echanges
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

        lines.append({'nom':f.projet.client.nom,'date':f.date_commande,'num_armoire':f.projet.num_armoire,'adresse1':f.projet.client.adresse1,'adresse2':f.projet.client.adresse2,'code_postal':f.projet.client.code_postal,\
        'ville':f.projet.client.ville,'revendeur':f.projet.revendeur.nom,'forfait':f.categorie_forfait})
    
    
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
"""/************************
	* Fonction __order_by
	* fonction interne
	* @brief fonction retourne une liste ordonnee à partir de la session dédiée au tri
	* @position fonction interne
	* @authentification non
	* @portee private
	*************************"""
def __order_by(liste,sort):
	if sort['sens']=='desc' :
		sens="-"
	else:
		sens=""
	return liste.order_by("%s%s" % (sens,sort['field']))
	
"""/*************************
	* View page
	* procedure
	* @brief procedure gerant l'affichage d'une page en particulier
	* @position indefinie
	* authentification oui
	* @role            utilisateur
	/************************/"""

def page(request):

	if request.POST:

		try:
			filtre=request.session['filtres']
			items=Projet.objects.all()
			filtered_items=apply_filter(items,filtre)
			items=__order_by(filtered_items,request.session['sort'])
		except Exception as error:
			print(error)
			items=Projet.objects.all()

		num_page=int(request.POST['num_page'])
		pager=Pager(items,'projects',num_page=num_page,nb_items_page=request.session['nb_items']).paginate()

		reponse=json.dumps({'liste':[projet_compose_liste(p) for p in pager[0]],
							'pagination': pager[1],
							'total_elts':pager[2],
							})

		return HttpResponse(reponse)

def nb(request):
	r=request.POST.copy()
	request.session['nb_items']=int(r['nb'])
	try:
		filtre=request.session['filtres']
		items=Projet.objects.all()
		filtered_items=apply_filter(items,filtre)
		items=__order_by(filtered_items,request.session['sort'])
	except Exception as error:
		print(error)
		items=Projet.objects.all()
	pager=Pager(items,'sessions',num_page=1,nb_items_page=request.session['nb_items']).paginate()

	return render(request,'dashboard/liste.html',{'liste':[projet_compose_liste(p) for p in pager[0]],
												'pagination':pager[1],
												'total_elts':pager[2],
												'nb':request.session['nb_items'],
												})
def search(request):
	request.session['filtres']=[{}]
	filtre=filter_construct(request.POST,SEARCH_TERMS)
	request.session['filtres']=filtre
	items=Projet.objects.all()
	filtered_items=apply_filter(items,filtre)
	items=filtered_items.order_by('-num_armoire')
	pager=Pager(items,'projects',nb_items_page=request.session['nb_items']).paginate()

	datas={'liste':[projet_compose_liste(c) for c in pager[0]],
			'pagination':pager[1],
			'total_elts':pager[2],}
	return HttpResponse(json.dumps(datas))
"""/*************************
	* View sort
	* procedure
	* @brief procedure permettant de trier les donnees avant de les redonner au serveur
	* @position indefinie
	* authentification oui
	* @role            utilisateur
	/************************/"""

def sort(request):
	r=request.POST.copy()
	request.session['sort']={'field':BASE_FIELDS[r['field']],'sens':r['sens']}
	try:
		filtre=request.session['filtres']
		items=Item.objects.all()
		filtered_items=apply_filter(items,filtre)
		items=__order_by(filtered_items,request.session['sort'])
	except Exception as error:
		print(error)
		items=Projet.objects.all()
	pager=Pager(items,'sessions',num_page=1,nb_items_page=request.session['nb_items']).paginate()
	reponse=json.dumps({'liste':__parse_items_json(pager[0]),
						'indices':__liste_indices(),
						'pagination': pager[1],
						'total_elts':pager[2],
						})
	return HttpResponse(reponse)
	
def add(request):
	form=ContactForm()
	return render(request,'dashboard/forms/form.html',{'form':form.as_table()})
	
def edit(request):
	pass
	
def save(request):
	pass
