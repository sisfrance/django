from suiviprojets.helpers.helpers import ZeepClient
import json
from  functools import reduce
CLIENTS = ['association_jean_baptiste_thierry','apbp','cocirelpokky','espace_casher','thierry_muller_espace_vert','fein_france',]
#CLIENTS = ['espace_casher']
def ZeendocCheck():
	
	for c in CLIENTS:
		z=ZeepClient(c,'check@sisfrance.eu','qV"B]S3T?%9F34s',"1")
		print("nbdocs:%s//size:%s" % (z.getNbDocs(),z.getVolumeDocs()))
		
		
if __name__== "__main__":
	
	ZeendocCheck()
	

	
	
