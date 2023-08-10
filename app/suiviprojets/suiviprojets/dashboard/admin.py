from django.contrib import admin
from suiviprojets.dashboard.models import Projet,TypePrestation,CategorieForfait,Flux,Forfait,TypeEchange,Echange,Contact \
										,StatutTache, Tache,Consommation,Prestation,Client,Intervenant,Revendeur,TypeProjet \
										,Task, TaskType
# Register your models here.

"""class SessionAdmin(admin.ModelAdmin):
	list_display=('id','source','date','sport_type','start_time')
	list_display_link=('id',)
	list_filter=('sport_type','source')
	search_fields=('id',)
	ordering=['-date','-start_time']
class ElevationAdmin(admin.ModelAdmin):
	list_display=('id','session',)
	search_fields=('session__id',)"""
	
	
class ProjetAdmin(admin.ModelAdmin):
	"""def add_view(self,request):
		try:
			id=request.GET['id']
			if id != None:
				self.client=Client.objects.get(pk=id)		
		except Exception as error :
			pass"""
	pass
		
class ConsoAdmin(admin.ModelAdmin):
	list_display=('id','date','nb_docs','volume_docs','forfait')
	
class EchangeAdmin(admin.ModelAdmin):
	list_display=('id','contact','projet','statut','temps_passe')

class PrestationAdmin(admin.ModelAdmin):
	list_display=('type_prestation','projet','date_programmee','date_realisation','statut')

class TacheAdmin(admin.ModelAdmin):
	list_display=('date_programmee','projet','nom','date_realisation','statut')

class TaskAdmin(admin.ModelAdmin):
	list_display=('statut','task_type','id','contact')
	
admin.site.register(TypePrestation)
admin.site.register(CategorieForfait)
admin.site.register(Flux)
admin.site.register(TypeEchange)
admin.site.register(Echange, EchangeAdmin)
admin.site.register(Forfait)
admin.site.register(Contact)
admin.site.register(StatutTache)
admin.site.register(Tache, TacheAdmin)
admin.site.register(Consommation,ConsoAdmin)
admin.site.register(Prestation, PrestationAdmin)
admin.site.register(Projet,ProjetAdmin)
admin.site.register(Client)
admin.site.register(Intervenant)
admin.site.register(Revendeur)
admin.site.register(TypeProjet)
admin.site.register(Task,TaskAdmin)
admin.site.register(TaskType)
