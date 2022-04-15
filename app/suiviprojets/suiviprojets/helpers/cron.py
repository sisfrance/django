from django_cron import CronJobBase,Schedule
from suiviprojets.dashboard.models import Projet,Forfait,Consommation
from suiviprojets.helpers.helpers import ZeepClient

class ZeendocCheckCronJob(CronJobBase):
	RUN_EVERY_MINS = 40
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code='suiviprojets_helpers_cron_ZeendocCheckCronJob'
	
	def do(self):
		projets=Projet.objects.filter(type_projet=1)
		for projet in projets:
			try:
				forfait=Forfait.objects.filter(projet=projet.id).order_by("-date_commande")[0]
				api=ZeepClient(forfait.url,'check@sisfrance.eu','qV"B]S3T?%9F34s',forfait)
				datas={'forfait':forfait,
					'nb_docs':api.nb_docs,
					'volume_docs':api.size,
					}
				conso=Consommation(**datas)
				conso.save()
			except Exception as e:
				print(e)
			
