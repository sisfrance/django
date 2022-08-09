#-*- coding: utf-8 -*-
import os
import math
import re
from zeep import Client,Settings,xsd
from zeep.transports import Transport
import json
from functools import reduce
from operator import itemgetter
from datetime import datetime,date,timedelta
from random import getrandbits,randrange
from django.db.models import Q
from django.forms.models import model_to_dict

def generatecolor():
	color="#"
	for i in range(0,2):
		color+=hex(randrange(255)).split('x')[1]
	print(color)
	return color

		
	

def divide(a,b):
	if b==0:
		return 0
	else:
		return a/b
"""/************************
   * Fonction clear_fieldnames
   * fonction
   * @brief fonction qui nettoie les noms de champs de la feuille excel pour limiter
   les risques d'incompatibilité
   * @return la chaine correctement formattée <string>
   * @portee publique
   **************************"""
def clear_fieldnames(chaine):
    chaine=strip_accents(chaine)
    chaine=re.sub("([° ,\',\/,\?,\.])?(\\n)?","",chaine)
    chaine=re.sub(" ","",chaine).lower()
    return chaine
"""/************************
   * Fonction nb_lines
   * fonction
   * @brief fonction qui renvoie le nombre de ligne du fichier csv
   * @return nb de lignes <int>
   * @portee publique
   **************************"""

def nb_lines(content):
    """lines=os.stat(filename).st_size"""
    with open(filename) as f:
        buf_size = 1024 * 1024
        read_f = f.read
        buf = read_f(buf_size)
        while buf:
             lines += buf.count('\n')
             buf = read_f(buf_size)
        f.close()
    return lines


"""/************************
   * Fonction apply_filter
   * fonction
   * @brief fonction qui renvoie le resultat des filtres appliqués aux données préchargées
   * @return tableau de données
   * @portee publique
   **************************"""


def apply_filter(items,filtre):

    for condition in filtre:
        if(isinstance(condition,Q)):
            items=items.filter(condition)
        else:
            items=items.filter(**condition)
    return items

"""/************************
   * Fonction filter_construct
   * fonction
   * @brief fonction qui formate la requete de filtres en un filtre pret à l'emploi pour django
   * @return <array>elts Q, dernier élement <dict></array>
   * @portee publique
   **************************"""

def filter_construct(requete,terms):

    filtreQ=[]
    filtres={}
    for key in requete:
        if key != 'csrfmiddlewaretoken' and key != 'nozeros' and terms[key] != None:
            print(terms[key])
            if re.match("^(\w+)(\[\])$",key):
                filtres[terms[key.replace("[]","")]]=requete.getlist(key)
            elif isinstance(terms[key],Q):
                filtreQ.append(terms[key])
            elif (key in ['date_debut','date_fin'] and verif_date(requete[key])):
                dateeval=list(map(lambda x: int(x),requete[key].split('/')))
                filtres[terms[key]]=datetime(dateeval[2],dateeval[1],dateeval[0]).strftime("%Y-%m-%d")
            else:
                filtres[terms[key]]=requete[key]

    filtreQ.append(filtres)

    return filtreQ

""" *******************************
* @function line number
* @brief renvoie la valeur de ligne d'apres \
*        la valeur du champ d'un objet donné
* @return valeur de ligne <int>
********************************"""

def line_number(valeur,liste,champ):
       i=0
       while i < len(liste):
           if liste[i].__dict__[champ] == valeur:
               return i
           else:
               i+=1
""" *******************************
* @function clean_string
* @brief permet d'enlever les accents des mots pour une verif
*
* @return string
********************************"""
def clean_string(val):
    rules=[(" ",""),
            ("!",""),
            ("\.",""),
            ("\?",""),
            ("'","")]
    for rule in rules:
        val=re.sub(re.compile(rule[0]),rule[1],val)
    val=strip_accents(val)
    return val

import unicodedata

def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")

    return str(text)

""" *******************************
* @function truncate_words
* @brief permet de réduire à un texte à ses x premiers mots
*
* @return valeur de ligne <int>
********************************"""

def truncate_words(value,nb,id=0):
    try:
        words=value.split(" ")
        if (len(words)>nb):
            if(id>0):
                uid=str(getrandbits(50))
                suite="<a class='td-zoom' id='"+uid+"' data-id='"+str(id)+"'>...suite...</a>"
                return " ".join(words[:10])+suite
            else:
               return " ".join(words[:10])
        else:
            return value
    except Exception as error:
        raise error

""" *******************************
* @function verif_date
* @brief permet de vérifier la validité d'une date
* @param my_date <date> à évaluer
* @return <boolean>
********************************"""

def verif_date(my_date):

    date_format = '%d/%m/%Y'
    try :
        valid_date = datetime.strptime(my_date, date_format)
        return True
    except ValueError:
        raise "%s n'est pas une date valide !" % my_date
        return False

""" *******************************
* @function last_month
* @brief permet de sortir le mois et l'annee d'une date
* @param my_date <date> à évaluer
* @return <tuple> (<string>,<string>)
********************************"""

def last_month(my_date):
    if(my_date.month==1):
        month=12
        year=my_date.year-1
    else:
        month=my_date.month-1
        year=my_date.year
    return (str.zfill(str(month),2), \
            str.zfill(str(year),4))

""" *******************************
* @function last_trimestre
* @brief permet de sortir le dernier trimestre achevé
* @param my_date <date> à évaluer
* @return <tuple> (<string>,<string>)
********************************"""

def last_trimestre(my_date):
    current_trimestre=math.ceil(my_date.month/4)
    if(current_trimestre==1):
        last_trimestre=4
        year=my_date.year-1
    else:
        last_trimestre=current_trimestre-1
        year=my_date.year
    return (str(last_trimestre), \
            str.zfill(str(year),4))
""" *******************************
* @function tab_trimestre
* @brief permet de creer un tableau de mois
* @param numero du trimestre <int> compris entre 1 et 4
* @return tableau<int>
********************************"""
def tab_trimestre(index):
    index=int(index)
    if index in [1,2,3,4]:
        end=index*3
        trimestre=[str(x) for x in range(end-2,end+1)]
        return trimestre
    else:
        return False

""" *******************************
* @function dictfetchall
* @brief permet de formatter en dictionnaire le resultat d'une requete sql brute
* @param resultat <result> à évaluer
* @return <dict>
********************************"""
def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
""" ***********************************
* @class Pager
* @brief objet gerant une barre de pagination a partir d'un groupe d'objets a afficher
* @params tableau_valeurs <Array> defini le groupe d'objets à paginer
*         url_objet       <String> la chaine de caracteres pour definir
*                                  l'url sur laquelle cliquer sur un des elements de la barre de pagination
*         num_page        <int> correspond à la page par defaut sur laquelle se placer. si id_objet defini
*                               le num_page correspondant sera cherché
*         nb_groupe_pages <int> nombre de groupes de pages à afficher sous le tableau avant flèches
*         nb_items_pages  <int> nombre d'items du tableau à afficher par page
*         id_objet        <int> l'id de l'objet courant s'il y en a (lors d'une recherche par exemple
*
* @methods paginate <public> renvoie un tuple de tableaux
*          __lien   <private> renvoie les liens formates à paginate
*
************************************"""

class Pager:

    def __init__(self,tableau_valeurs,url_objet,num_page=1,nb_groupe_pages=5,nb_items_page=10,id_objet=None):
        self.tableau_valeurs=tableau_valeurs
        self.url_objet=url_objet
        self.num_page=num_page
        self.nb_groupe_pages=nb_groupe_pages
        self.nb_items_page=nb_items_page
        self.id_objet=id_objet

    def __lien(self,indice_page,item='',valeur=None):
        if not valeur:
            valeur=indice_page
        if item == 'disabled':
            lien=''
            li_class="page-item disabled"
            a_class="page-link disabled"
            id='disabled-'+str(indice_page)
        elif item !='':
            lien="href='/%s/page/%s'" % (self.url_objet,indice_page)
            li_class='page-item'
            a_class="page-link"
            id=item
        else:
            lien="href='/%s/page/%s'" % (self.url_objet,indice_page)
            li_class='page-item'
            a_class="page-link"
            id='lien-page-'+str(indice_page)
        if indice_page == self.num_page:
            id='lien-page-active'
            li_class="page-item active"
            a_class="page-link"
        return "<li id='li-%s' class=\"%s\"><a id=%s class=\"%s\" %s data-page='%s'>%s</a></li>" % (id,li_class,id,a_class,lien,indice_page,valeur)

    def paginate(self):

        try:
            liste=self.tableau_valeurs
            """ si l'objet passe a un id, on cherche le num_page correspondant"""
            if self.id_objet:
                try:
                    index=[i.id for i in liste].index(self.id_objet)
                except:
                    index=[i['id'] for i in liste].index(self.id_objet)
                self.num_page=int(math.floor(index/self.nb_items_page))+1

            """ calculs nombre de pages """

            nb_items=len(liste)
            #print("nb_items="+str(nb_items))
            nb_pages=int(math.ceil(float(nb_items)/float(self.nb_items_page)))
            #print("nb_pages="+str(nb_pages))
            """ mise en indices des indices d'objets qui constitueront la page"""

            indice_first=(self.num_page-1)*self.nb_items_page
            indice_last=(indice_first+self.nb_items_page)
            #print("indice_first="+str(indice_first))
            #print("indice_last="+str(indice_last))
            """ slice de la liste d'objets """

            liste_items=liste[indice_first:indice_last]
            if len(liste_items)==0 and self.num_page-2 >=0 :
                indice_first=(self.num_page-2)*self.nb_items_page
                indice_last=(indice_first+self.nb_items_page)

            """****************************** """
            """ creation de la liste de liens, Pages """
            """****************************** """

            if self.num_page > nb_pages or self.num_page < 0 :
                self.num_page=1

            """indice du groupe de la page et du dernier groupe de pages """

            indice_groupe=int(math.floor((self.num_page-1)/self.nb_groupe_pages))
            last_groupe=int(math.floor((nb_pages-1)/self.nb_groupe_pages))


            """ creation des footers de pagination """
            if nb_pages < self.nb_groupe_pages+1:
                footer="</ul>"
            else:
                footer=self.__lien(((indice_groupe+1)*self.nb_groupe_pages)+1,"plus-one",'&#9654;')+self.__lien(nb_pages,"last",'&#9654;&#9654;')+"</ul>"
            initial_id=((indice_groupe)*self.nb_groupe_pages)+1
            final_id=initial_id+self.nb_groupe_pages

            """ creation des pages """

            if final_id > nb_pages:
                inter_id=nb_pages+1
                liens="".join([self.__lien(i) for i in range(initial_id,inter_id)])
                liens=liens+"".join([self.__lien(i,'disabled') for i in range(inter_id,final_id)])
            else:
                liens="".join([self.__lien(i) for i in range(initial_id,final_id)])

            if indice_groupe == 0:
                liens="<ul class='liste-pages pagination'>"+liens+footer
            elif indice_groupe == last_groupe:
                liens="<ul class='liste-pages pagination'>"+self.__lien(1,"first",'&#9664;&#9664;')+self.__lien(((indice_groupe-1)*self.nb_groupe_pages+1),"minus-one",'&#9664;')+liens+"</ul>"
            else :
                liens="<ul class='liste-pages pagination'>"+self.__lien(1,"first",'&#9664;&#9664;')+self.__lien(((indice_groupe-1)*self.nb_groupe_pages+1),"minus-one",'&#9664;')+liens+footer
           
            return liste_items,liens,nb_items
        except Exception as error:
            print(error)
            print("erreur de pagination")
            return [],[],0

""" ***********************************
* @class ZeepClient
* @brief objet permettant d'aller chercher des informations via l'api de zeendoc
* @params tableau_valeurs <Array> defini le groupe d'objets à paginer
*         url      <String> la chaine de caracteres pour definir
*                                  l'url sur laquelle cliquer sur un des elements de la barre de pagination
*         user     <string> identifiant utilisateur
*         mdp      <string> mot de passe
*         classeurs <string> liste des classeurs sous forme de chaine de caractères séparés par des virgules
*
* @methods paginate <public> renvoie un tuple de tableaux
*          __lien   <private> renvoie les liens formates à paginate
*
************************************"""

class ZeepClient():
	def __init__(self,url,user,mdp,forfait):
		self.url=url
		self.user=user
		self.mdp=mdp
		try:
			self.classeurs=forfait.classeurs.split(";")
		except Exception as e:
			self.classeurs=forfait.split(";")
		self.nb_docs=0
		self.size=0
		self.settings=Settings(strict=False,xml_huge_tree=True)
		try:
			transport=Transport(operation_timeout=800,timeout=800)
			self.client=Client("https://armoires.zeendoc.com/"+self.url+"/ws/0_7/wsdl.php?wsdl",transport=transport,settings=self.settings)
			print("######CLIENT :"+self.url+"##########")
			self.__ask()
			print("######FIN"+self.url+"######")
		except Exception as e:
			print("Erreur client"+self.url)
			print(str(e))
			print("########")
			pass
			
	def __create_request_data(self,coll):
		return {'Login':self.user,
					'Password':'',
					'CPassword':self.mdp,
					'Coll_Id':'coll_'+coll,
					'Get_PDF_FileSize':1,
					'IndexList':[{'Index':{
									'Id':1,
									'Label':'N_Status',
									'Value':'-2',
									'Operator':'ABOVE'
									}
								 }
								],
					'StrictMode':0,
					'Order_Col':'',
					'saved_query':"",
					'Order':'ASC',
					'Query_Operator':"",
					'From':0,
					'Nb_Results':"",
					'Get_Original_FileSize':1,
					'Get_Comments':0,
					'Get_History':0,
					'Get_Shipment_Status':0,
									
				}
	def __ask_classeur(self,id_classeur):
		print("je parse le classeur "+id_classeur)
		requests_datas=self.__create_request_data(id_classeur)
		i=1
		bool=False
		try:
			while bool == False and i < 5:
				response=self.client.service.searchDoc(**requests_datas)
				try:
					datas=json.loads(response)
					bool=True
				except Exception as e:
					i+=1
				print(i)
					
		except Exception as error:
			print(str(error))
		
		dictDatas=dict(datas)
		
		try:
			nb_docs=dictDatas['Nb_Docs']
		except Exception as error:
			print("expection_ask_classeur : nb_docs "+str(error))
			nb_docs=0
			

		documents=dictDatas['Document']
		Adocuments=[]
		#Bdocuments=[]
		for doc in documents:
			try:
				#Bdocuments.append(int(doc['FileSize_PDF']))
				Adocuments.append(int(doc['FileSize_Original']))
			except Exception as err:
				print(err)
			
		size=round(reduce(lambda a,b: a+b,[d for d in Adocuments])/1000000,2)
		#sizecomp=round(reduce(lambda a,b: a+b,[d for d in Bdocuments])/1000000,2)
			
		print("classeur %s nb_docs:%s size:%s " % (id_classeur,nb_docs,size))
		
		return {'nb_docs':nb_docs,'size':size}
		
	def __ask(self):
		
		for coll in self.classeurs:
			result=self.__ask_classeur(coll)
			self.nb_docs+=result['nb_docs']
			self.size+=result['size']
			
	def getNbDocs(self):
		return round(self.nb_docs,0)
		
	def getVolumeDocs(self):
		return round(self.size,2)
			
	def show_conso(self):
		return 'nombre de documents : %s / taille totale : %s' % (self.nb_docs,self.size)
		
			


