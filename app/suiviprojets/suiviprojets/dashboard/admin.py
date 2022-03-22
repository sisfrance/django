from django.contrib import admin
from suiviprojets.dashboard.models import Projet,TypePrestation,CategorieForfait,Flux,Forfait,TypeEchange,Echange,Contact \
										,StatutTache, Tache,Consommation,Prestation,Client,Intervenant,Revendeur
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
		
admin.site.register(TypePrestation)
admin.site.register(CategorieForfait)
admin.site.register(Flux)
admin.site.register(TypeEchange)
admin.site.register(Echange)
admin.site.register(Forfait)
admin.site.register(Contact)
admin.site.register(StatutTache)
admin.site.register(Tache)
admin.site.register(Consommation)
admin.site.register(Prestation)
admin.site.register(Projet,ProjetAdmin)
admin.site.register(Client)
admin.site.register(Intervenant)
admin.site.register(Revendeur)
