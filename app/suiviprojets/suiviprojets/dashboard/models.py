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
    num_armoire=models.CharField(max_length=125)
    adresse1=models.TextField(null=True,blank=True)
    adresse2=models.TextField(null=True,blank=True)
    code_postal=models.CharField(max_length=10,null=True,blank=True)
    ville=models.CharField(max_length=50,null=True,blank=True)
    revendeur=models.ForeignKey(Revendeur,on_delete=models.SET_NULL, null=True,blank=True)

    def __str__(self):
        return self.nom+"-"+self.num_armoire   
         
class Forfait(models.Model):
    id=models.AutoField(primary_key=True)
    date_commande=models.DateField()
    client= models.ForeignKey(Client,on_delete=models.SET_NULL,null=True,blank=True)
    categorie_forfait= models.ForeignKey(CategorieForfait,on_delete=models.SET_NULL,null=True,blank=True)
    def __str__(self):
        return self.client.nom+"-"+self.categorie_forfait.categorie_forfait
              


class Consommation(models.Model):
    id=models.AutoField(primary_key=True)
    date=models.DateField()
    client=models.ForeignKey(Client,on_delete=models.SET_NULL,null=True,blank=True)
    nb_docs=models.IntegerField(null=True,blank=True)
    volume_docs=models.IntegerField(null=True,blank=True)
    
    def __str__(self):
        return self.client+"-"+nb_docs

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
    client=models.ForeignKey(Client,on_delete=models.SET_NULL,null=True,blank=True)
    type_prestation=models.ForeignKey(TypePrestation,on_delete=models.SET_NULL,null=True,blank=True)
    intervenant=models.ForeignKey(Intervenant,on_delete=models.SET_NULL,null=True,blank=True)
    date_programmee=models.DateField(null=True,blank=True)
    date_realisation=models.DateField(null=True,blank=True)
    statut=models.ForeignKey(StatutTache,on_delete=models.SET_NULL,null=True, blank=True,default=1)
    notes=models.TextField(null=True,blank=True)
    
    def __str__(self):
        return self.client.nom+"-"+self.type_prestation.type_prestation

class Tache(models.Model):
    id=models.AutoField(primary_key=True)
    client=models.ForeignKey(Client,on_delete=models.SET_NULL,null=True,blank=True)
    nom=models.CharField(max_length=150)
    date_programmee=models.DateField(null=True,blank=True)
    date_echeance=models.DateField(null=True,blank=True)
    date_realisation=models.DateField(null=True,blank=True)
    statut=models.ForeignKey(StatutTache,on_delete=models.SET_NULL,null=True,blank=True,default=1)
    temps_passe=models.CharField(max_length=20,null=True,blank=True)
    description=models.TextField(null=True,blank=True)
    personnes_en_charge=models.ManyToManyField(Intervenant,null=True,blank=True)
    
    def __str__(self):
        return self.nom+"-"+self.client.nom

class Contact(models.Model):
    id=models.AutoField(primary_key=True)
    client=models.ForeignKey(Client,on_delete=models.SET_NULL,null=True,blank=True)
    nom=models.CharField(max_length=50)
    prenom=models.CharField(max_length=30,null=True,blank=True)
    email =models.EmailField(max_length=150,null=True,blank=True)
    tel = models.CharField(max_length=150,null=True,blank=True)
    notes=models.CharField(max_length=255,null=True,blank=True)
    
    def __str__(self):
        return self.nom+" "+self.prenom

class TypeEchange(models.Model):
    id=models.AutoField(primary_key=True)
    type_echange=models.CharField(max_length=50)
    
    def __str__(self):
        return self.type_echange
            
class Echange(models.Model):
    id=models.AutoField(primary_key=True)
    contact=models.ForeignKey(Contact,on_delete=models.SET_NULL,null=True,blank=True)
    date=models.DateField(null=True,blank=True)
    heure=models.TimeField(null=True,blank=True)
    type_echange=models.ForeignKey(TypeEchange,on_delete=models.SET_NULL,null=True,blank=True)
    statut=models.ForeignKey(StatutTache,on_delete=models.SET_NULL,null=True,blank=True,default=1)
    notes=models.TextField()
    
    def __str__(self):
        return self.type_echange.type_echange+"-"+self.contact.nom+"-"+self.contact.prenom
