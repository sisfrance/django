import simplejson as json
import csv
import mimetypes
import os
import re
import math
from django.conf import settings
from operator import itemgetter
import itertools
from functools import reduce
from datetime import datetime, date, timedelta
from django.http import Http404, HttpResponse, StreamingHttpResponse, HttpResponseRedirect,JsonResponse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum,Q
from django.db.models.functions import ExtractMonth, ExtractYear
from django.forms.models import model_to_dict
from suiviprojets.dashboard.models import TaskType, Projet,TypeProjet,TypePrestation,CategorieForfait,Flux,Forfait,TypeEchange,Echange,Contact,Task,TaskType \
                                            ,StatutTache, Tache,Consommation,Prestation,Client, Intervenant
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
SEARCH_FIELDS_KANBAN={'projet':'projet__in',
					'intervenant':'intervenant__in',
					'client':'client',
					'statut':'statut__in',
					'task_type':'task_type__in',
					}
					
SEARCH_FIELDS_KANBAN_PROJET={'statut':'statut__in',
							'intervenant':'intervenant__in',
							'task_type':'task_type__in',
							}
SEARCH_TERMS_PROJETS={'num_armoire':'num_armoire__icontains',
			'nom':'client__nom__icontains',
			'forfait':'forfait_id',
			}
			
SEARCH_TERMS_CLIENTS={'nom':'nom__icontains',
					'ville':'ville__icontains',
					}
					
SCRIPTS=['common','node_modules/fullcalendar/main.min','jquery_soap','node_modules/jquery-xml2json/src/xml2json','index']
STYLES=['js/node_modules/chart.js/dist/Chart.min.css',
		'js/node_modules/fullcalendar/main.min.css','scss/styles.css']

def __init__():
	pass
	
def kanban_construct(elements,status):
	return {s:elements.filter(statut=s.id).order_by('-date_programmee')for s in status}
	
def determineTempsPasse(id_projet):
	tp_ech=Task.objects.filter(projet=id_projet,task_type=3).aggregate(Sum('temps_passe'))
	tp_tac=Task.objects.filter(projet=id_projet,task_type=2).aggregate(Sum('temps_passe'))
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
			"echanges":[ str(t.date_programmee)+" : "+str(t.contact.nom) for t in Task.objects.filter(projet=p.id,task_type=3).exclude(statut__in=[4])],
			"prestations":[t.nom for t in Task.objects.filter(projet=p.id,task_type=1).exclude(statut__in=[4])],
			"taches":[t.nom for t in Task.objects.filter(projet=p.id,task_type=2,statut__statut='realisée')],
			}
	
	"""taches=Tache.objects.filter(projet=p.id,statut__statut='en cours')
	echanges=Echange.objects.filter(contact__client_id=client.id,date__gt=date.today()).order_by('-date')
	prestations=Prestation.objects.filter(projet=p.id,statut__statut__in=['en attente','en cours'])
	
	projet['echanges']=[str(e.date)+":"+str(e.contact.nom) for e in echanges]
	projet['prestations']=[str(pres.type_prestation)+":"+str(pres.statut.statut) for pres in prestations]
	projet['taches']=[t.nom for t in taches]"""
	
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
	""" @function define_alert
	    @brief  Traitement des alertes
				conso_nb_jours    >  80% -> rouge
				conso_volume_docs >  80% -> rouge
				conso_nb_docs     >  80% -> rouge
				conso_nb_docs/conso_nb_jours > 1,3
				conso_volume_docs / conso_nb_jours >1,3 
				
				conso_volume_docs > conso_nb_jours -> jaune
				conso_nb_docs     > conso_nb_jours -> jaune
				
				@conso : conso_volume_docs ou conso_nb_docs
				@conso_jours : conso_nb jours
				@seuil_forfait : 80%
				@seuil_compare : 1,3
	
	"""
	pass
	
	def define_alert(conso,conso_jours,seuil_forfait,seuil_compare):
		if (float(conso) > float(seuil_forfait)) or (float(conso_jours) > float(seuil_compare)) or (float(conso) / float(conso_jours) > float(seuil_compare)):
			alert="red"
		elif float(conso) /float(conso_jours) > 1:
			alert="yellow"
		else:
			alert="green"
			
		print(alert)
		return alert
		
	try:
		forfait=Forfait.objects.filter(projet=id_projet).order_by("-date_commande")[0]
		
		consommation=Consommation.objects.filter(forfait=forfait.id).order_by("-date")[0]
		nb_jours_consommes=(consommation.date-forfait.date_commande).days
		conso_nb_jours =nb_jours_consommes / int(forfait.categorie_forfait.duree*365)
		
		
		nb_docs=int(consommation.nb_docs)
		volume_docs=consommation.volume_docs
		
		
		if forfait.categorie_forfait.flux.flux=="flux":
			conso_volume_docs=volume_docs/(forfait.categorie_forfait.volume*1000*int(forfait.categorie_forfait.duree))
			conso_nb_docs="/"
			alert=define_alert(conso_volume_docs,conso_nb_jours,0.8,1.3)
		elif forfait.categorie_forfait.flux.flux=="documents":
		
			conso_volume_docs="/"
			conso_nb_docs=(nb_docs/(forfait.categorie_forfait.volume*int(forfait.categorie_forfait.duree)))
			alert=define_alert(conso_nb_docs,conso_nb_jours,0.8,1.3)
		else:
			pass
		
		
		
		conso = {
				'conso_nb_jours': "{:.1f} %".format(conso_nb_jours*100),
				'nb_jours':nb_jours_consommes,
				'volume_docs':"{:.1f} Go".format(volume_docs/1000),
				'nb_docs':nb_docs,
				'conso_volume_docs': conso_volume_docs != "/" and "{:.1f} %".format(conso_volume_docs*100 )or "/" ,
				'conso_nb_docs': conso_nb_docs != "/" and "{:.1f} %".format(conso_nb_docs*100) or "/" ,
				'alert':alert,
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
				'alert':'red',
				}
	
	return conso
	

def projet_compose_details(id):
	
	instance_projet=Projet.objects.get(pk=id)
	projet={"id":instance_projet.id,
			"date_creation":instance_projet.date_creation.strftime("%Y-%m-%d"),
			"date_fin_programmee":instance_projet.date_fin_programmee.strftime("%Y-%m-%d"),
			"client":{"id":instance_projet.client.id, \
					"nom":instance_projet.client.nom, \
					"adresse1":instance_projet.client.adresse1, \
					"adresse2":instance_projet.client.adresse2, \
					"code_postal":instance_projet.client.code_postal, \
					"ville":instance_projet.client.ville \
					},
			"type_projet":{"id":instance_projet.type_projet.id, \
							"type_projet":str(instance_projet.type_projet)},
			"num_armoire":instance_projet.num_armoire
			}
	"""client=instance_projet.client"""
	projet['forfait']=Forfait.objects.filter(projet=id).order_by('-date_commande')[0]
	projet['contacts']=Contact.objects.filter(client=instance_projet.client.id,type_projet=instance_projet.type_projet.id).order_by("nom","prenom")
	
	"""taches=Tache.objects.filter(projet_id=id)
	echanges=Echange.objects.filter(contact__client_id=client.id).order_by('-date')
	prestations=Prestation.objects.filter(projet=id)
	
	
	projet['taches']=taches
	projet['contacts']=contacts
	projet['forfait']=forfait
	projet['echanges']=echanges
	projet['prestations']= prestations"""
	
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
	
	"""tasks=Tache.objects.filter(projet_id=id,statut__statut__in=["à programmer","en attente","en cours"])
	tasks_events={'events':[{'title':t.nom,'start':str(t.date_programmee),'statut':t.statut.color,'description':t.description} for t in tasks],'color':'green','textColor':'white'}
	
	prestations=Prestation.objects.filter(projet_id=id,statut__statut__in=["en attente","à programmer","en cours"])
	prestations_events={'events':[{'title':p.type_prestation.type_prestation,'start':str(p.date_programmee),'statut':p.statut.color,'description':p.notes} for p in prestations],'color':'green','textColor':'white'}

	echanges=Echange.objects.filter(contact__client_id=projet['client']['id'],statut__statut__in=["en attente","à programmer","en cours"])
	echanges_events={'events':[{'title':e.type_echange.type_echange,'statut':e.statut.color,'start':str(e.date),'description':e.notes} for e in echanges],'color':'light-green','textColor': 'white'}
	
	projet['eventsct']=json.dumps(tasks_events)
	projet['eventscp']=json.dumps(prestations_events)
	projet['eventsce']=json.dumps(echanges_events)"""

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
	request.session['espace']='accueil'
	statuts=StatutTache.objects.exclude(id__in=[4]).order_by('statut')
	filtres={'intervenants':Intervenant.objects.all().order_by('nom','prenom'),
			'projets':Projet.objects.all().order_by('client__nom'),
			'statuts':StatutTache.objects.all().order_by('statut'),
			'tasks_types':TaskType.objects.all().order_by('type_task'),
			}
	"""if request.session.get('filtres') == None:
		request.session['sort']={'field':'date','sens':'desc'}
		request.session['nb_items']=10
		request.session['filtres']=[{}]
		request.session['message']=""
		request.session['actions']=[]"""
		
	""" Préparation du kanban """
	
	""" Préparation des taches ou prestation à effectuer """
	
	
	kanban=kanban_construct(Task.objects.all(),statuts)
	largeur_col=math.floor(12/len(statuts))-1
	largeur_separateur=math.floor((12-len(statuts)*largeur_col)/2)
	toprogram_prestations=Task.objects.filter(Q(task_type=1) & Q(statut__statut__in=["en attente","à programmer"])|Q(date_programmee__isnull=True)).values('projet__client__nom','nom','id')
	toprogram_tasks=Task.objects.filter(Q(task_type=2) & Q(statut__statut__in=["en attente","à programmer"]) | Q(date_programmee__isnull=True)).values('projet__client__nom','nom','id')
	next_echanges=Task.objects.filter(Q(task_type=3) & Q(statut__statut__in=["en attente","à programmer"])).values('contact__nom','contact__prenom','date_programmee','heure','nom','id')
	
	clients=[]
	
	for pr in toprogram_prestations:
		if pr['projet__client__nom'] not in clients:
			clients.append(pr['projet__client__nom'])
			

	datas={'partial':'dashboard/kanban.html',
			'status':statuts,
			'kanban':kanban,
			'largeur_col':largeur_col,
			'largeur_separateur':largeur_separateur,
			'toprogram_prestations':toprogram_prestations,
			'toprogram_tasks':toprogram_tasks,
			'next_echanges':next_echanges,
			'filtres':filtres,
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
	request.session['espace']='projets'

			
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
	
	statuts=StatutTache.objects.exclude(id__in=[4]).order_by('statut')
	if(len(statuts)!=0):
		largeur_col=math.floor(12/len(statuts))-1
		largeur_separateur=math.floor((12-len(statuts)*largeur_col)/2)
	else:
		largeur_col=0
		largeur_separateur=6
	projet=projet_compose_details(id)
	
	tasks_events=Task.objects.filter(projet=id,date_programmee__isnull=False,date_echeance__isnull=False)
	tasks_dates=Task.objects.filter(projet=id,date_programmee__isnull=False)
	tasks=Task.objects.filter(projet=id)
	
	""" events s'affiche dans la timeline du bas """
	events=[{'start':(t.date_programmee != None) and t.date_programmee.strftime('%Y-%m-%d') or "",
			'end':(t.date_echeance != None) and t.date_echeance.strftime('%Y-%m-%d') or "",
			'notes':t.description,
			'nom':t.nom,
			'row':t.task_type.id,
			'bgColor':t.task_type.color,
			} for t in tasks_events]
	""" dates s'affichent dans le calendrier """
	dates={'events':[{'title':td.nom,'statut':td.statut.color,'start':str(td.date_programmee),'row':td.task_type.id,'description':td.description ,'color':td.task_type.color} for td in tasks_dates]  ,'textColor': 'white' }
	
	datas={'partial':'dashboard/details_projet.html',
			'projet':projet,
			'kanban':kanban_construct(tasks,statuts),
			'filtres':{'statuts':StatutTache.objects.all().order_by('id'),
						'intervenants':Intervenant.objects.all().order_by('nom','prenom'),
						'tasks_types':TaskType.objects.all().order_by('type_task'),
						},
			'largeur_col':largeur_col,
			'temps_passe':determineTempsPasse(id),
			'nb_lignes':len(TaskType.objects.all()),
			'events':events,
			'dates':json.dumps(dates),
			'largeur_separateur':largeur_separateur,
			'styles':['js/jquery.timeline-master/dist/jquery.timeline.min.css']+STYLES,
			'scripts':SCRIPTS+['jquery.timeline-master/dist/jquery.timeline.min'],
			}
	return render(request,"index.html",datas)
	
def tache_show(request,id):
	task=Task.objects.get(pk=id)
	datas={
			'task':task,
			}
	return render(request,'dashboard/show.html',datas)
	
def clients(request):
	
	request.session['sort']={'field':'nom','sens':'desc'}
	request.session['nb_items']=10
	request.session['filtres']=[{}]
	request.session['message']=""
	request.session['actions']=[]
	request.session['espace']='clients'
	
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
		tp_ech=Task.objects.filter(projet=p["id"],type_task='3').aggregate(Sum('temps_passe'))
		tp_tac=Task.objects.filter(projet=p["id"],type_task='2').aggregate(Sum('temps_passe'))
		p['temps échanges']=tp_ech['temps_passe__sum']
		p['temps installation']=tp_tac['temps_passe__sum']
		
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

def noms_domaines(request):
	tableau_domaines=[]
	contacts=Contact.objects.all()
	for c in contacts:
		if c.email != None and c.email !="" :
			ma=re.match(r"^(\w+[ \. | \- | \_ ]?\w*)*\@((\w+[ \. | \- | \_ ]?\w*)*\.\w+)$",c.email)
			if ma.group(2) not in tableau_domaines:
				tableau_domaines.append({"client":c.client.nom,"nom_domaine":ma.group(2)})
	labels=["client","nom_domaine"]
	tempfile="/".join([settings.TMP_ROOT,"domainestmp.csv"])
	
	with open(tempfile,"a") as fichier:
		writer=csv.DictWriter(fichier,fieldnames=labels,delimiter=";",dialect="excel")
		writer.writeheader()
		for t in tableau_domaines:
			writer.writerow(t)
		fichier.close()
	
	filec=open(tempfile,"r")

	response=HttpResponse(FileWrapper(filec),content_type=mimetypes.guess_type(filec.name)[0])
	response['Content-Disposition']='attachment; filename='+filec.name
	os.remove(tempfile)
	return response
	
def __parse_items(espace,items):
	lines=[]
	if espace == 'accueil':
		projets=items.values('projet').distinct()
		print(espace)
		for p in Projet.objects.filter(id__in=projets):
			next_echange=Task.objects.filter(projet=p.id,task_type=1,statut__statut='en cours').last()
			lines.append({"nom":p.client.nom,
						"num_armoire":p.num_armoire,
						"temps_passe":determineTempsPasse(p.id),
						"taches_en_cours":"\n".join(["-".join([t.date_programmee.strftime("%d/%m/%Y"),t.description]) for t in items.filter(projet=p.id,task_type=2,statut__statut='en cours').order_by('date_programmee')]),
						"taches_realisees":"\n".join(["-".join([t.date_programmee.strftime("%d/%m/%Y"),t.description]) for t in items.filter(projet=p.id,task_type=2,statut__statut='réalisée').order_by('date_realisation')]),
						"taches_en_attente":"\n".join([t.description for t in items.filter(projet=p.id,task_type=2,statut__statut__in=['en attente','à programmer']).order_by('date_echeance')]),
						"prestations_en_cours":"\n".join(["-".join([t.date_programmee.strftime("%d/%m/%Y"),t.description]) for t in items.filter(projet=p.id,task_type=1,statut__statut__in='en cours').order_by('date_echeance')]),
						"prestations_realisees":"\n".join(["-".join([t.date_programmee.strftime("%d/%m/%Y"),t.description]) for t in items.filter(projet=p.id,task_type=1,statut__statut__in='réalisée').order_by('date_echeance')]),
						"prochain_echange": next_echange and " - ".join([next_echange.date_programmee.strftime("%d/%m/%Y"),next_echange.description]) or "",
						"forfait":str(Forfait.objects.filter(projet=p.id).last().categorie_forfait),
						})
		labels=['nom','num_armoire','temps_passe','taches_en_cours','taches_realisees','taches_en_attente','prestations_en_cours','prestations_realisees','prochain_echange','forfait']
	elif espace =='clients':
		pass
	elif espace =='projets':
		pass
	else:
		labels=['nom','date','num_armoire','adresse1','adresse2','code_postal','ville','revendeur','forfait']
		
	return (labels,lines)
	
def download(request):

	filtre=request.session['filtres']
	espace=request.session['espace']
	if espace == 'accueil':
		modele=Task
	elif espace == 'clients':
		modele=Client
	elif espace == 'projets':
		modele=Projet
	else:
		modele=Forfait
		
	elements=modele.objects.all()
	filtered_items=apply_filter(elements,filtre)
	its=__parse_items(espace,filtered_items)
	labels=its[0]
	lines=its[1]
	
	
	"""lines=[]
	i=0
	for f in Forfait.objects.all().order_by('id'):
		i+=1

		lines.append({'nom':f.projet.client.nom,'date':f.date_commande,'num_armoire':f.projet.num_armoire,'adresse1':f.projet.client.adresse1,'adresse2':f.projet.client.adresse2,'code_postal':f.projet.client.code_postal,\
		'ville':f.projet.client.ville,'revendeur':f.projet.revendeur.nom,'forfait':f.categorie_forfait})"""
	
	
	"""lines=[{'nom':f.client.nom,'date':f.date_commande,'num_armoire':f.client.num_armoire,'adresse1':f.client.adresse1,'adresse2':f.client.adresse2,'code_postal':f.client.code_postal,\
	'ville':f.client.ville,'revendeur':f.client.revendeur.nom,'forfait':f.categorie_forfait} for f in Forfait.objects.all().order_by('client__num_armoire')]"""
	
	"""labels=['nom','date','num_armoire','adresse1','adresse2','code_postal','ville','revendeur','forfait']"""

	"""tempfile="/".join([settings.TMP_ROOT,"datastmp.csv"])"""
	tempfile="-".join(['datas-projets',espace,datetime.now().strftime("%Y%m%d%H%M"),".csv"])

	with open(tempfile,"a",encoding='utf-8-sig') as fich:
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
	request.session['espace']='projets'
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
	request.session['espace']='clients'
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

def accueil_search(request):
	r=request.POST.copy()
	try:
		projet_id=r["projet_id"]
		tasks=Task.objects.filter(projet=projet_id).order_by('-date_programmee')
		modele_filtre=SEARCH_FIELDS_KANBAN_PROJET
		exclude_keys=['projet_id']
	except Exception as error:
		tasks=Task.objects.all().order_by('-date_programmee')
		modele_filtre=SEARCH_FIELDS_KANBAN
		exclude_keys=[]
	
	
	filtre=filter_construct(request.POST,modele_filtre,exclude_keys)
	request.session['filtres']=filtre
	request.session['espace']='accueil'
	statuts=StatutTache.objects.all()
	
	try:
		if len(r.getlist('statut[]'))!= 0 :
			statuts=statuts.filter(id__in=r.getlist('statut[]'))
		else:
			statuts=statuts.exclude(id__in=[4])
	except Exception as error:
		statuts=statuts.exclude(id__in=[4])

	
	
	kanban=apply_filter(tasks,filtre)
	
	k={s:kanban.filter(statut=s.id).order_by('-date_programmee')for s in statuts}
	
	"""echs=apply_filter(Echange.objects.all(),filtre)
	prests=apply_filter(Prestation.objects.all(),filtre)
	tachs=apply_filter(Tache.objects.all(),filtre)"""
	
	
	"""statuts=StatutTache.objects.all()"""
	
	if(len(statuts)!=0):
		largeur_col=math.floor(12/len(statuts))-1
		largeur_separateur=math.floor((12-len(statuts)*largeur_col)/2)
	else:
		largeur_col=0
		largeur_separateur=6
		
	"""for s in statuts :
		echanges[s.statut]=echs.filter(statut=s.id).order_by('-date')
		taches[s.statut]=tachs.filter(statut=s.id).order_by('-date_programmee')
		prestations[s.statut]=prests.filter(statut=s.id).order_by('-date_programmee')"""
	datas={'partial':'dashboard/kanban.html',
			'status':statuts,
			'largeur_col':largeur_col,
			'largeur_separateur':largeur_separateur,
			'kanban':k,
			}
	return render(request,'partiel_kanban.html',datas)
	

def create_model_mask(objet):
	if objet=='contact':
		mask = {'model':Contact,'form':ContactForm,'template':'partiel_client','fields':[{'field':'client',
															'model':Client,
															},
															{'field':'type_projet',
															'model':TypeProjet
															}]}
	elif objet=='echange':
		mask = {'model':Task,'form':EchangeForm,'template':'partiel_echange','fields':[{'field':'projet',
															'model':Projet
															}]}
	elif objet=='prestation':
		mask = {'model':Task,'form':PrestationForm,'template':'partiel_prestation','fields':[{'field':'projet',
																	'model':Projet
																	}]}
	elif objet=='tache':
		mask = {'model':Task,'form':TacheForm,'template':'partiel_tache','fields':[{'field':'projet',
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
		type_projet=r['type_projet']
	except Exception:
		type_projet=""
	try:
		client=r['client']
	except Exception:
		client=''
		
	datas={"id":"",
			"id_projet":r['projet'],
			"id_type_projet":type_projet,
			"id_client":client,
			"objet":r['objet'],
			"form":form.as_p()
			}
	return render(request,'dashboard/forms/form.html',datas)
	
def edit(request):
	r=request.POST.copy()
	mask=create_model_mask(r['objet'])
	instance=mask['model'].objects.get(pk=r['id'])
	form=mask['form'](instance=instance)
	datas={"id":instance.id,
			"projet":r['projet'],
			"objet":r['objet'],
			"form":form.as_p()
			}
	return render(request,'dashboard/forms/form.html',datas)
	
def save(request):
	r=request.POST.copy()
	mask=create_model_mask(r['objet'])

	if r['id'] != '-1':
		instance=mask['model'].objects.get(pk=r['id'])
		form=mask['form'](r,instance=instance)
	else:
		if r['objet'] != 'contact':
			instance=mask['model'](task_type=TaskType.objects.get(type_task=r['objet']))
			form=mask['form'](r,instance=instance)
		else:
			form=mask['form'](r)
	if form.is_valid():
		form.save()

		datas={'result':'done',
				'content':'/projet/'+r['projet']+'/'
				}
	else:
		try:
			type_projet=r['type_projet']
		except Exception:
			type_projet=""
		try:
			client=r['client']
		except Exception:
			client=''
		rendu = render_to_string('dashboard/forms/form.html',{"id":r['id'],
															"id_projet":r['projet'],
															"id_type_projet":type_projet,
															"id_client":client,
															"objet":r['objet'],
															"form":form.as_p()
														})
		datas= {'result':'fail',
				'content':rendu
				}
	return HttpResponse(json.dumps(datas))

