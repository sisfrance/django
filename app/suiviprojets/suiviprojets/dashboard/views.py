import simplejson as json
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
from suiviprojets.dashboard.forms import ContactForm,PrestationForm,TacheForm,EchangeForm
from suiviprojets.helpers.helpers import apply_filter, filter_construct, Pager,ZeepClient
from wsgiref.util import FileWrapper



# Create your views here.
MOIS=[{'tag':'janvier','days':31},{'tag':'février','days':29},{'tag':'mars','days':31}, \
		{'tag':'avril','days':30},{'tag':'mai','days':31},{'tag':'juin','days':30}, \
		{'tag':'juillet','days':31},{'tag':'août','days':31},{'tag':'septembre','days':30}, \
		{'tag':'octobre','days':31},{'tag':'novembre','days':30},{'tag':'décembre','days':31}]
		
BASE_FIELDS_PROJETS={'id':'id',
			'num_armoire':'num_armoire',
			'type_projet':'type_projet',
			'client':'client',
			}
			
BASE_FIELDS_CLIENTS={'id':'id',
			'nom':'nom',
			'ville':'ville',
			}
			
SEARCH_TERMS_PROJETS={'num_armoire':'num_armoire__icontains',
			'nom':'client__nom__icontains',
			'forfait':'forfait_id',
			}
			
SEARCH_TERMS_CLIENTS={'nom':'nom__icontains',
					'ville':'ville__icontains',
					}
					
SCRIPTS=['common','node_modules/fullcalendar/main.min','index','jquery_soap','node_modules/jquery-xml2json/src/xml2json']
STYLES=['js/node_modules/chart.js/dist/Chart.min.css',
		'js/node_modules/fullcalendar/main.min.css','scss/styles.css']

def __init__():
	pass

def determineTempsPasse(id_projet):
	tp_ech=Echange.objects.filter(projet=id_projet).aggregate(Sum('temps_passe'))
	tp_tac=Tache.objects.filter(projet=id_projet).aggregate(Sum('temps_passe'))
	temps_echanges=transformToDays(tp_ech['temps_passe__sum'])
	temps_installation=transformToDays(tp_tac['temps_passe__sum'])
	print("%s jours echanges, %s jours installation" % (temps_echanges,temps_installation))
	return "%s jours echanges, %s jours installation" % (temps_echanges,temps_installation)

def transformToDays(hours):
	if hours is None :
		return "0 j"
	else:
		d = hours //8
		h = hours % 8 
	return str(int(d))+" j, "+str(int(h))+" h"

def projet_compose_liste(p):
	client=p.client
	
	projet={"id":p.id,
			"client":{'nom':p.client.nom,'id':p.client.id},
			"type_projet":str(p.type_projet),
			"num_armoire":p.num_armoire,
			}
	
	taches=Tache.objects.filter(projet=p.id,statut__statut='en cours')
	echanges=Echange.objects.filter(contact__client_id=client.id,date__gt=date.today()).order_by('-date')
	prestations=Prestation.objects.filter(projet=p.id,statut__statut__in=['en attente','en cours'])
	
	projet['echanges']=[str(e.date)+":"+str(e.contact.nom) for e in echanges]
	projet['prestations']=[str(pres.type_prestation)+":"+str(pres.statut.statut) for pres in prestations]
	projet['taches']=[t.nom for t in taches]
	
	""" Traitement de la consommation """
	
	if(p.type_projet.id == 1):
		forfait=Forfait.objects.filter(projet=p.id).order_by('-date_commande')[0]
		
		try:
			projet['debut_forfait']=str(forfait.date_commande)
			projet['categorie_forfait']=forfait.categorie_forfait.categorie_forfait
		except Exception as error:
			projet['debut_forfait']=""
			projet['categorie_forfait']=""
		
		consommation=calcul_consommation(p.id)
		
		for k,v in consommation.items():
			projet[k]=v
		
	return projet

def calcul_consommation(id_projet):
	try:
		forfait=Forfait.objects.filter(projet=id_projet).order_by("-date_commande")[0]
		
		consommation=Consommation.objects.filter(forfait=forfait.id).order_by("-date")[0]
		nb_jours_consommes=(consommation.date-forfait.date_commande).days
		conso_nb_jours = "{:.1f} %".format(nb_jours_consommes / int(forfait.categorie_forfait.duree*365)*100)
		
		nb_docs=int(consommation.nb_docs)
		f_volume_docs=consommation.volume_docs/1000
		volume_docs="{:.1f} Go".format(f_volume_docs)
		
		
		if forfait.categorie_forfait.flux.flux=="flux":
			conso_volume_docs="{:.1f} %".format((f_volume_docs/(forfait.categorie_forfait.volume*int(forfait.categorie_forfait.duree)))*100)
			conso_nb_docs="N/D"
			
		elif forfait.categorie_forfait.flux.flux=="documents":
		
			conso_volume_docs="N/D"
			conso_nb_docs="{:.1f} %".format((nb_docs/(forfait.categorie_forfait.volume*int(forfait.categorie_forfait.duree)))*100)
			
		else:
			pass
		
		
		conso = {
				'conso_nb_jours':conso_nb_jours,
				'nb_jours':nb_jours_consommes,
				'volume_docs':volume_docs,
				'nb_docs':nb_docs,
				'conso_volume_docs':conso_volume_docs,
				'conso_nb_docs':conso_nb_docs,
				}

	except Exception as err:
		print(err)
		conso = {
				'conso_nb_jours':-1,
				'nb_jours':-1,
				'volume_docs':-1,
				'nb_docs':-1,
				'conso_volume_docs':-1,
				'conso_nb_docs':-1,
				
				}
	return conso
	

def projet_compose_details(id):
	instance_projet=Projet.objects.get(pk=id)
	projet={"id":instance_projet.id,
			"client":{"id":instance_projet.client.id,"nom":instance_projet.client.nom},
			"type_projet":{"id":instance_projet.type_projet.id,"type_projet":str(instance_projet.type_projet)},
			"num_armoire":instance_projet.num_armoire
			}
			
	client=instance_projet.client
	forfait=Forfait.objects.filter(projet=id).order_by('-date_commande')[0]
	taches=Tache.objects.filter(projet_id=id)
	echanges=Echange.objects.filter(contact__client_id=client.id).order_by('-date')
	prestations=Prestation.objects.filter(projet=id)
	contacts=Contact.objects.filter(client=instance_projet.client.id,type_projet=instance_projet.type_projet.id).order_by("nom")
	
	projet['taches']=taches
	projet['contacts']=contacts
	projet['forfait']=forfait
	projet['echanges']=echanges
	projet['prestations']= prestations
	
	if instance_projet.type_projet.id == 1:
		projet['consommation']=calcul_consommation(id)
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
	
def client_compose_liste(c):
	client={'id':c.id,
			'nom':c.nom,
			'adresse1':c.adresse1,
			'adresse2':c.adresse2,
			'code_postal':c.code_postal,
			'ville':c.ville
			}
	projets=Projet.objects.filter(client=c.id).values('type_projet__type_projet','id').order_by('type_projet')
	contacts=Contact.objects.filter(client=c.id).values('nom','prenom','id').order_by('nom','prenom')
	client['Dprojets']=[{"type_projet":p["type_projet__type_projet"],"id":p["id"]} for p in projets]
	client['projets']=','.join(["<a href='/projet/"+str(p["id"])+"'>"+str(p["type_projet__type_projet"])+"</a>" for p in projets])
	client['Dcontacts']=[{"nom":ct["nom"],"prenom":ct["prenom"],"id":ct["id"]} for ct in contacts]
	client['contacts']=','.join(["<span>%s %s</span>" % (ct["nom"],ct["prenom"]) for ct in contacts])
	return client

def client_compose_detail(c):
	contacts=Contact.objects.filter(client=c.id).order_by('nom')
	client={"id":c.id,
			"nom":c.nom,
			"adresse1":c.adresse1,
			"adresse2":c.adresse2,
			"code_postal":c.code_postal,
			"ville":c.ville,
			"projets":[{'id':p.id,'type_projet':p.type_projet,'num_armoire':p.num_armoire,'temps_passe':determineTempsPasse(p.id)} for p in Projet.objects.filter(client=c.id)],
			"contacts":[{"id":con.id,
						"nom":con.nom,
						"prenom":con.prenom,
						"tel":con.tel,
						"email":con.email,
						} for con in contacts]
			}
	projets=[p['id'] for p in client['projets']]
	""" parsage des evenements """
	""" un evenement se compose 
		-title
		-start
		-end
		l'ensemble des events peut avoir les propriétés
		color
		background-color"""
	tasks=Tache.objects.filter(projet_id__in=projets,statut__statut__in=["à programmer","en attente","en cours"])
	tasks_events={'events':[{'title':t.nom,'start':str(t.date_programmee),'statut':t.statut.color,'description':t.description} for t in tasks],'color':'green','textColor':'white'}
	
	prestations=Prestation.objects.filter(projet_id__in=projets,statut__statut__in=["en attente","à programmer","en cours"])
	prestations_events={'events':[{'title':p.type_prestation.type_prestation,'start':str(p.date_programmee),'statut':p.statut.color,'description':p.notes} for p in prestations],'color':'green','textColor':'white'}

	echanges=Echange.objects.filter(contact__client_id=c.id,statut__statut__in=["en attente","à programmer","en cours"])
	echanges_events={'events':[{'title':e.type_echange.type_echange,'statut':e.statut.color,'start':str(e.date),'description':e.notes} for e in echanges],'color':'light-green','textColor': 'white'}
	
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

			
	projets=__order_by(Projet.objects.all(),request.session['sort'])
	pagination=Pager(projets,"projets").paginate()
	
	Dprojets=[projet_compose_liste(p) for p in pagination[0]]

	datas={'partial':'dashboard/liste_projets.html',
			'projets':Dprojets,
			'total_elts':pagination[2],
			'pagination':pagination[1],
			'scripts':SCRIPTS,
			'styles':STYLES,}
	return render(request,"index.html",datas)
	
def details_projet(request,id):
	projet=projet_compose_details(id)
	datas={'partial':'dashboard/details_projet.html',
			'projet':projet,
			'styles':STYLES,
			'scripts':SCRIPTS,}
	return render(request,"index.html",datas)

def clients(request):
	
	request.session['sort']={'field':'nom','sens':'desc'}
	request.session['nb_items']=10
	request.session['filtres']=[{}]
	request.session['message']=""
	request.session['actions']=[]
	
	clients=Client.objects.all().order_by('nom')
	pagination=Pager(clients,"clients").paginate()
	Dclients=[client_compose_liste(c) for c in pagination[0]]
	datas={'partial':'dashboard/liste_clients.html',
			'clients':Dclients,
			'scripts':SCRIPTS,
			'pagination':pagination[1],
			'total_elts':pagination[2],
			'styles':STYLES,
	}
	return render(request,'index.html',datas)
		
def details_client(request,id):
	client=Client.objects.get(pk=id)
	c=client_compose_detail(client)

	datas={'partial':'dashboard/details_client.html',
			'client':c,
			'scripts':SCRIPTS+['node_modules/fullcalendar-scheduler/main'],
			'styles':STYLES+['js/node_modules/fullcalendar-scheduler/main.css'],
			}
	return render(request,"index.html",datas)
	

	
def currents(request):
	events_tasks = [{"id":t.id,"resourceId":t.projet.client.id,"resourceTitle":t.projet.client.nom,"title":t.nom,"color":"green","start":str(t.date_programmee),"end":str(t.date_realisation),"statut":t.statut.color,"description":t.description} for t in Tache.objects.filter(statut__statut__in=['en attente','en cours'],date_programmee__isnull=False)]
	events_prestations = [{"id":p.id,"resourceId":p.projet.client.id,"resourceTitle":p.projet.client.nom,"title":str(p.type_prestation),"color":"pink","start":str(p.date_programmee),"end":str(p.date_realisation),"statut":p.statut.color,"description":p.notes} for p in Prestation.objects.filter(statut__statut__in=['en attente','en cours'],date_programmee__isnull=False)]
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
	
def temps_passe(request):
	""" Requete permettant de recuperer le temps passe par projets """
	projets=[{"id":p.id,"client":p.client.nom,"revendeur":p.revendeur.nom } for p in Projet.objects.all()]
	
	for p in projets:
		tp_ech=Echange.objects.filter(projet=p["id"]).aggregate(Sum('temps_passe'))
		tp_tac=Tache.objects.filter(projet=p["id"]).aggregate(Sum('temps_passe'))
		p['temps échanges']=transformToDays(tp_ech['temps_passe__sum'])
		p['temps installation']=transformToDays(tp_tac['temps_passe__sum'])
		
	labels=['id','client','revendeur','temps échanges','temps installation',]
	tempfile="/".join([settings.TMP_ROOT,"tempstmp.csv"])
	
	with open(tempfile,"a") as fich:
		writer=csv.DictWriter(fich,fieldnames=labels,delimiter=";",dialect='excel')
		writer.writeheader()
		for p in projets:
			writer.writerow(p)
		fich.close()

	filec=open(tempfile,"r")

	response=HttpResponse(FileWrapper(filec),content_type=mimetypes.guess_type(filec.name)[0])
	response['Content-Disposition']='attachment; filename='+filec.name
	os.remove(tempfile)

	return response
    
    
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

def projets_page(request):

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
		pager=Pager(items,'projets',num_page=num_page,nb_items_page=request.session['nb_items']).paginate()
		""" Attention envoi en json donc il faut laisser les tags liste et pagination """
		reponse=json.dumps({'liste':[projet_compose_liste(p) for p in pager[0]],
							'pagination': pager[1],
							'total_elts':pager[2],
							})

		return HttpResponse(reponse)

def projets_nb(request):
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
	pager=Pager(items,'projets',num_page=1,nb_items_page=request.session['nb_items']).paginate()

	return render(request,'dashboard/liste_projets.html',{'projets':[projet_compose_liste(p) for p in pager[0]],
												'pagination':pager[1],
												'total_elts':pager[2],
												'nb':request.session['nb_items'],
												})
def projets_search(request):
	request.session['filtres']=[{}]
	filtre=filter_construct(request.POST,SEARCH_TERMS_PROJETS)
	request.session['filtres']=filtre
	items=Projet.objects.all()
	filtered_items=apply_filter(items,filtre)
	items=filtered_items.order_by('-id')
	pager=Pager(items,'projets',nb_items_page=request.session['nb_items']).paginate()

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

def projets_sort(request):
	r=request.POST.copy()
	request.session['sort']={'field':BASE_FIELDS_PROJETS[r['field']],'sens':r['sens']}
	try:
		filtre=request.session['filtres']
		items=Projet .objects.all()
		filtered_items=apply_filter(items,filtre)
		items=__order_by(filtered_items,request.session['sort'])
	except Exception as error:
		print(error)
		items=Projet.objects.all()
	pager=Pager(items,'projets',num_page=1,nb_items_page=request.session['nb_items']).paginate()
	reponse=json.dumps({'liste':[projet_compose_liste(p) for p in pager[0]],
						'pagination': pager[1],
						'total_elts':pager[2],
						})
	return HttpResponse(reponse)
	
def clients_page(request):
	if request.POST:

		try:
			filtre=request.session['filtres']
			items=Client.objects.all()
			filtered_items=apply_filter(items,filtre)
			items=__order_by(filtered_items,request.session['sort'])
		except Exception as error:
			print(error)
			items=Client.objects.all()

		num_page=int(request.POST['num_page'])
		pager=Pager(items,'clients',num_page=num_page,nb_items_page=request.session['nb_items']).paginate()

		reponse=json.dumps({'liste':[client_compose_liste(p) for p in pager[0]],
							'pagination': pager[1],
							'total_elts':pager[2],
							})

		return HttpResponse(reponse)

def clients_nb(request):	
	r=request.POST.copy()
	request.session['nb_items']=int(r['nb'])
	try:
		filtre=request.session['filtres']
		items=Client.objects.all()
		filtered_items=apply_filter(items,filtre)
		items=__order_by(filtered_items,request.session['sort'])
	except Exception as error:
		print(error)
		items=Client.objects.all()
	pager=Pager(items,'clients',num_page=1,nb_items_page=request.session['nb_items']).paginate()
	return render(request,'dashboard/liste_clients.html',{'clients':[client_compose_liste(p) for p in pager[0]],
												'pagination':pager[1],
												'total_elts':pager[2],
												'nb':request.session['nb_items'],
												})
	
def clients_search(request):
	request.session['filtres']=[{}]
	filtre=filter_construct(request.POST,SEARCH_TERMS_CLIENTS)
	request.session['filtres']=filtre
	items=Client.objects.all()
	filtered_items=apply_filter(items,filtre)
	items=filtered_items.order_by('-id')
	pager=Pager(items,'clients',nb_items_page=request.session['nb_items']).paginate()

	datas={'liste':[client_compose_liste(c) for c in pager[0]],
			'pagination':pager[1],
			'total_elts':pager[2],}
	return HttpResponse(json.dumps(datas))
	
def clients_sort(request):
	r=request.POST.copy()
	request.session['sort']={'field':BASE_FIELDS_CLIENTS[r['field']],'sens':r['sens']}
	try:
		filtre=request.session['filtres']
		items=Client.objects.all()
		filtered_items=apply_filter(items,filtre)
		items=__order_by(filtered_items,request.session['sort'])
	except Exception as error:
		print(error)
		items=Client.objects.all()
	pager=Pager(items,'clients',num_page=1,nb_items_page=request.session['nb_items']).paginate()
	reponse=json.dumps({'liste':[client_compose_liste(p) for p in pager[0]],
						'pagination': pager[1],
						'total_elts':pager[2],
						})
	return HttpResponse(reponse)

def create_model_mask(objet):
	if objet=='contact':
		mask = {'model':Contact,'form':ContactForm,'fields':[{'field':'client',
															'model':Client
															},
															{'field':'type_projet',
															'model':TypeProjet
															}]}
	elif objet=='echange':
		mask = {'model':Echange,'form':EchangeForm,'fields':[{'field':'projet',
															'model':Projet
															}]}
	elif objet=='prestation':
		mask = {'model':Prestation,'form':PrestationForm,'fields':[{'field':'projet',
																	'model':Projet
																	}]}
	elif objet=='tache':
		mask = {'model':Tache,'form':TacheForm,'fields':[{'field':'projet',
														'model':Projet
														}]}
	else:
		mask = {}
	return mask
	
def add(request):
	
	r=request.POST.copy()
	mask=create_model_mask(r['objet'])
	args={}

	for f in mask['fields']:
		if r[f['field']] != '':
			args[f['field']]=f['model'].objects.get(pk=r[f['field']])
	new_instance=mask['model'](**args)
	form=mask['form'](instance=new_instance)
	if r['objet']== 'echange':
		projet=Projet.objects.get(pk=r['projet'])
		queryset=Contact.objects.filter(client=projet.client.id,type_projet=projet.type_projet.id).order_by('nom')
		form.fields['contact'].queryset=queryset
	try:
		value=r['client']
	except Exception:
		value=''
		
	datas={"id":"",
			"id_projet":r['projet'],
			"id_client":value,
			"objet":r['objet'],
			"form":form.as_p()
			}
	return render(request,'dashboard/forms/form.html',datas)
	
def edit(request):
	r=request.POST.copy()
	mask=create_model_mask(r['objet'])
	instance=mask['model'].objects.get(pk=r['id'])
	form=mask['form'](instance=instance)
	datas={"id":r['id'],
			"id_projet":r['projet'],
			"id_client":r['client'],
			"objet":r['objet'],
			"form":form.as_p()
			}
	return render(request,'dashboard/forms/form.html',datas)
	
def save(request):
	r=request.POST.copy()
	mask=create_model_mask(r['objet'])
	if r['id'] != '-1':
		instance=mask['model'].objects.get(pk=r['id'])
		form=mask['form'](r,instance)
	else:
		form=mask['form'](r)
	if form.is_valid():
		form.save()	
		return HttpResponseRedirect('/project/'+r['projet']+'/')
	else:
		return render(request,'dashboard/forms/form.html',{'form':form.as_p()})

	
