"""import sharepy as share"""
import json
import datetime
from django.conf import settings
import suiviprojets.dashboard.models as m


URL='https://sisfranceeu0.sharepoint.com'
USER_NAME='connect@sisfranceeu0.onmicrosoft.com'
PASSWD='C0n33!#Mt'    

def set_date_start():
	projets=m.Projet.objects.all()
	for p in projets:
		date_creation = m.Forfait.objects.filter(projet=p.id)[0].date_commande
		date_fin_programmee = date_creation + datetime.timedelta(days=360)
		p.date_creation=date_creation
		p.date_fin_programmee=date_fin_programmee
		p.save()
		print(str(date_creation) + "/" +str(date_fin_programmee))

def convert_echanges():
	echanges=m.Echange.objects.all()
	i=0
	for e in echanges:
		datas={'nom':str(e.type_echange)+":"+str(e.contact)+":"+str(e.date),
				'projet':e.projet,
				'date_programmee':e.date,
				'contact':e.contact,
				'heure':e.heure,
				'task_type':m.TaskType.objects.get(pk=3),
				'statut':e.statut,
				'temps_passe':e.temps_passe,
				'description':e.notes,}
		tache=m.Task(**datas)
		tache.save()
		i+=1
	print(str(i)+" echanges ont été convertis")

def convert_taches():
	taches=m.Tache.objects.all()
	i=0
	for t in taches:
		datas={'nom':t.nom,
			'projet':t.projet,
			'date_programmee':t.date_programmee,
			'date_echeance':t.date_echeance,
			'date_realisation':t.date_realisation,
			'task_type':m.TaskType.objects.get(pk=2),
			'statut':t.statut,
			'temps_passe':t.temps_passe,
			'description':t.description,}
		intervenants_id=[i.id for i in t.intervenant.all()]
		print(intervenants_id)
		intervenants=m.Intervenant.objects.filter(id__in=intervenants_id)
		tache=m.Task(**datas)
		tache.save()
		tache.intervenant.set(t.intervenant.all())
		
		i+=1
	print(str(i)+" taches ont été converties")
	
def convert_prestations():
	i=0
	prestations=m.Prestation.objects.all()
	for p in prestations:
		datas={'nom':str(p.type_prestation)+":"+str(p.projet),
				'projet':p.projet,
				'date_programmee':p.date_programmee,
				'date_realisation':p.date_realisation,
				'task_type':m.TaskType.objects.get(pk=1),
				'statut':p.statut,
				'notes':p.notes,}
		tache=m.Task(**datas)
		tache.save()
		i+=1
	print(str(i)+" prestations ont été converties")
	
"""class SharePointExplorer:
	
	def __init__(self,site):
		self.session=self.connecting()
		self.site=site
		self.result=[]

	def connecting(self):
		try:
			return share.connect(URL,USER_NAME,PASSWD)
		except Exception as error:
			print(error)
	
	def liste_files(self):
		response=self.session.get(URL+"/sites/"+self.site+"/_api/web/lists/getbytitle('Documents')/items?$select=FileLeafRef,FileRef&top=30")
		result=json.loads(response.text)
		self.result=result
		return [f["FileLeafRef"] for f in dict(result)['d']['results']]
		
	def liste_dir(self,partage="documents%20partages"):
		response=self.session.get(URL+"/sites/"+self.site+"/_api/web/lists/GetByTitle('Documents')/items?$filter=ContentType eq 'Folder'")
		result=json.loads(response.text)
		self.result=result
		return result
	

	def upload_files(self):
		headers = {"accept": "application/json;odata=verbose",
		"content-type": "application/x-www-urlencoded; charset=UTF-8"}
		fileToUpload = "/var/app/suiviprojets/suiviprojets/media/tmp"
		filename="toto1.txt"
		with open(fileToUpload+"/"+filename, 'rb') as read_file:
			content = read_file.read()
			print(content)
			url=URL+"/_api/web/getfolderbyserverrelativeurl('/sites/"+self.site+"/')/Files/add(url='"+filename+"',overwrite=true)"
			print(url)
			p = self.session.post(url, data=content, headers=headers)
			p =zeen.session.post("https://sisfranceeu0.sharepoint.com/sites/Zeendoc/_api/web/GetFoldersByServerRelativeUrl('/sites/Zeendoc/documents%20partages/')/Files/add(url='toto.txt',overwrite=true)",data=content,headers=headers)"""

if __name__=="__main__":
	"""cd=SharePointExplorer('Zeendoc')
	print(cd.liste_files())
	print(cd.liste_dir())
	cd.upload_files()"""
	convert_echanges()
	convert_taches()
	convert_prestations()
	set_date_start()
	
