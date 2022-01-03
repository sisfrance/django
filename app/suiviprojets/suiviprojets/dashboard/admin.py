from django.contrib import admin
from suiviprojets.dashboard.models import TypePrestation,CategorieForfait,Flux,Forfait,TypeEchange,Echange,Contact \
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
admin.site.register(Client)
admin.site.register(Intervenant)
admin.site.register(Revendeur)