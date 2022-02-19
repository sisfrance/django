#-*- coding:utf-8 -*-
import re
"""import floppyforms as forms"""
from django import forms
from django.forms import fields,widgets
from django.contrib import admin
from suiviprojets.dashboard.models import Tache,Prestation,Echange,Contact,Projet

class ProjetForm(forms.ModelForm):
	class Meta:
		model=Projet
		fields='__all__'

class TacheForm(forms.ModelForm):
	class Meta:
		model=Tache
		fields='__all__'

class PrestationForm(forms.ModelForm):
	class Meta:
		model=Prestation
		fields='__all__'

class EchangeForm(forms.ModelForm):
	class Meta:
		model=Echange
		fields='__all__'
		
class ContactForm(forms.ModelForm):
	class Meta:
		model=Contact
		fields='__all__'
		
