#-*- coding:utf-8 -*-
import re
"""import floppyforms as forms"""
from django import forms
from django.forms import fields,widgets
from django.contrib import admin
from suiviprojets.dashboard.models import Task,Tache,Prestation,Echange,Contact,Projet,TaskType

class ProjetForm(forms.ModelForm):
	class Meta:
		model=Projet
		fields='__all__'

class TacheForm(forms.ModelForm):
	
	class Meta:
		model=Task
		fields=['projet','nom','date_programmee','date_echeance','date_realisation','statut','temps_passe','description','intervenant','notes']

class PrestationForm(forms.ModelForm):
	task_type=fields.CharField(widget=forms.HiddenInput(attrs={"value":1}),required=False)
	
	class Meta:
		model=Task
		fields=['projet','nom','date_programmee','date_echeance','date_realisation','statut','temps_passe','description','intervenant','notes']

class EchangeForm(forms.ModelForm):
	task_type=fields.CharField(widget=forms.HiddenInput(attrs={"value":3}),required=False)
	
	class Meta:
		model=Task
		fields=['projet','nom','date_programmee','heure','statut','temps_passe','description','intervenant','contact','notes']
		
class ContactForm(forms.ModelForm):
	email=forms.CharField(widget=forms.TextInput)
	class Meta:
		model=Contact
		fields='__all__'

