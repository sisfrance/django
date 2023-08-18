from django.db import models
import datetime


# Create your models here.

class TypePrestation(models.Model):
    id=models.AutoField(primary_key=True)
    type_prestation=models.CharField(max_length=100)
    notes=models.TextField(null=True,blank=True)
    
    def __str__(self):
        return self.type_prestation

class Flux(models.Model):
    id=models.AutoField(primary_key=True)
    flux=models.CharField(max_length=50)
    
    def __str__(self):
        return self.flux

class CategorieForfait(models.Model):
    id=models.AutoField(primary_key=True)
    categorie_forfait=models.CharField(max_length=100)
    duree=models.IntegerField(null=True,blank=True)
    flux=models.ForeignKey(Flux,on_delete=models.SET_NULL,null=True,blank=True)
    volume=models.DecimalField(decimal_places=1,max_digits=6,null=True,blank=True)

    def __str__(self):
        return self.categorie_forfait

class Revendeur(models.Model):
	id=models.AutoField(primary_key=True)
	nom=models.CharField(max_length=100)
	notes=models.TextField(null=True,blank=True)
	
	def __str__(self):
		return self.nom

class Client(models.Model):
    id=models.AutoField(primary_key=True)
    nom=models.CharField(max_length=125)
    adresse1=models.TextField(null=True,blank=True)
    adresse2=models.TextField(null=True,blank=True)
    code_postal=models.CharField(max_length=10,null=True,blank=True)
    ville=models.CharField(max_length=50,null=True,blank=True)
    

    def __str__(self):
        return self.nom  

class TypeProjet(models.Model):
	id=models.AutoField(primary_key=True)
	type_projet=models.CharField(max_length=25)
	icone=models.CharField(max_length=2500,null=True,blank=True)
	
	def __str__(self):
		return self.type_projet

class Projet(models.Model):
    id=models.AutoField(primary_key=True)
    date_creation=models.DateField(null=True,blank=True)
    date_fin_programmee=models.DateField(null=True,blank=True)
    client=models.ForeignKey(Client,on_delete=models.SET_NULL,null=True,blank=True)
    type_projet=models.ForeignKey(TypeProjet,on_delete=models.SET_NULL,null=True,blank=True)
    num_armoire=models.CharField(max_length=125,null=True,blank=True)
    revendeur=models.ForeignKey(Revendeur,on_delete=models.SET_NULL, null=True,blank=True)
    def __str__(self):
        return str(self.client)+"-"+str(self.type_projet)
    
class Forfait(models.Model):
    id=models.AutoField(primary_key=True)
    date_commande=models.DateField()
    projet= models.ForeignKey(Projet,on_delete=models.SET_NULL,null=True,blank=True)
    url=models.CharField(max_length=50,null=True,blank=True)
    classeurs=models.CharField(max_length=150,null=True,blank=True)
    categorie_forfait= models.ForeignKey(CategorieForfait,on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self):
        return self.projet.client.nom+"-"+self.categorie_forfait.categorie_forfait
              


class Consommation(models.Model):
    id=models.AutoField(primary_key=True)
    date=models.DateField(auto_now_add=True)
    forfait=models.ForeignKey(Forfait,on_delete=models.SET_NULL,null=True,blank=True)
    nb_docs=models.IntegerField(null=True,blank=True)
    volume_docs=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    
    def __str__(self):
        return self.forfait.categorie_forfait.categorie_forfait+"Nb de documents::"+str(self.nb_docs)+";Volume :"+str(self.volume_docs)

class StatutTache(models.Model):
    id=models.AutoField(primary_key=True)
    statut=models.CharField(max_length=30)
    color=models.CharField(max_length=7,null=True,blank=True)
    
    def __str__(self):
        return self.statut
        
class Intervenant(models.Model):
    id=models.AutoField(primary_key=True)
    nom=models.CharField(max_length=150)
    prenom=models.CharField(max_length=75,null=True,blank=True)
    email=models.CharField(max_length=255,null=True,blank=True)
    tag=models.CharField(max_length=75,null=True,blank=True)
    notes=models.TextField(null=True,blank=True)

    def __str__(self):
        return self.nom+"-"+self.prenom
    
class Prestation(models.Model):
    id=models.AutoField(primary_key=True)
    projet=models.ForeignKey(Projet,on_delete=models.SET_NULL,null=True,blank=True)
    type_prestation=models.ForeignKey(TypePrestation,on_delete=models.SET_NULL,null=True,blank=True)
    intervenant=models.ForeignKey(Intervenant,on_delete=models.SET_NULL,null=True,blank=True)
    date_programmee=models.DateField(null=True,blank=True)
    date_realisation=models.DateField(null=True,blank=True)
    statut=models.ForeignKey(StatutTache,on_delete=models.SET_NULL,null=True, blank=True,default=1)
    notes=models.TextField(null=True,blank=True)
    
    def __str__(self):
        return self.projet.client.nom+"-"+self.type_prestation.type_prestation

class Tache(models.Model):
    id=models.AutoField(primary_key=True)
    projet=models.ForeignKey(Projet,on_delete=models.SET_NULL,null=True,blank=True)
    nom=models.CharField(max_length=150)
    date_programmee=models.DateField(null=True,blank=True)
    date_echeance=models.DateField(null=True,blank=True)
    date_realisation=models.DateField(null=True,blank=True)
    statut=models.ForeignKey(StatutTache,on_delete=models.SET_NULL,null=True,blank=True,default=1)
    temps_passe=models.CharField(max_length=20,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    intervenant=models.ManyToManyField(Intervenant,null=True,blank=True)
    
    def __str__(self):
        return self.nom+"-"+self.projet.client.nom


    
class Contact(models.Model):
    id=models.AutoField(primary_key=True)
    client=models.ForeignKey(Client,on_delete=models.SET_NULL,null=True,blank=True)
    type_projet=models.ForeignKey(TypeProjet,on_delete=models.SET_NULL,null=True,blank=True)
    nom=models.CharField(max_length=50)
    prenom=models.CharField(max_length=30,null=True,blank=True)
    email = models.EmailField(max_length=150,null=True,blank=True)
    tel = models.CharField(max_length=150,null=True,blank=True)
    notes=models.CharField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return str(self.nom)+" "+str(self.prenom)

class TypeEchange(models.Model):
    id=models.AutoField(primary_key=True)
    type_echange=models.CharField(max_length=50)
    
    def __str__(self):
        return self.type_echange
            
class Echange(models.Model):
    id=models.AutoField(primary_key=True)
    contact=models.ForeignKey(Contact,on_delete=models.SET_NULL,null=True,blank=True)
    projet=models.ForeignKey(Projet,on_delete=models.SET_NULL,null=True,blank=True)
    date=models.DateField(null=True,blank=True)
    heure=models.TimeField(null=True,blank=True)
    type_echange=models.ForeignKey(TypeEchange,on_delete=models.SET_NULL,null=True,blank=True)
    statut=models.ForeignKey(StatutTache,on_delete=models.SET_NULL,null=True,blank=True,default=1)
    temps_passe=models.CharField(max_length=20,null=True,blank=True,default="0")
    notes=models.TextField(null=True,blank=True)
    intervenant=models.ForeignKey(Intervenant, on_delete=models.SET_NULL,null=True,blank=True)
    
    def __str__(self):
        return self.type_echange.type_echange+"-"+str(self.contact.nom)+"-"+str(self.contact.prenom)

class TaskType(models.Model):
	id=models.AutoField(primary_key=True)
	type_task=models.CharField(max_length=150)
	tag=models.CharField(max_length=15,null=True,blank=True)
	color=models.CharField(max_length=8,null=True,blank=True)
	
	def __str__(self):
		return self.type_task
		
class Task(models.Model):
    id=models.AutoField(primary_key=True)
    projet=models.ForeignKey(Projet,on_delete=models.SET_NULL,null=True,blank=True)
    nom=models.CharField(max_length=150)
    task_type=models.ForeignKey(TaskType,on_delete=models.SET_NULL,null=True,blank=True)
    date_programmee=models.DateField(null=True,blank=True)
    heure=models.TimeField(null=True,blank=True)
    date_echeance=models.DateField(null=True,blank=True)
    date_realisation=models.DateField(null=True,blank=True)
    statut=models.ForeignKey(StatutTache,on_delete=models.SET_NULL,null=True,blank=True,default=1)
    temps_passe=models.CharField(max_length=20,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    intervenant=models.ManyToManyField(Intervenant,null=True,blank=True)
    contact=models.ForeignKey(Contact,on_delete=models.SET_NULL,null=True,blank=True)
    notes=models.TextField(null=True,blank=True)
    
    def __str__(self):
       return self.nom+"-"+self.projet.client.nom
