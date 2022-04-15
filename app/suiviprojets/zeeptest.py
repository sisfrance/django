from suiviprojets.helpers.helpers import ZeepClient
import json
from  functools import reduce

def ZeendocCheck():
	z=ZeepClient('association_jean_baptiste_thierry','check@sisfrance.eu','qV"B]S3T?%9F34s',"1;3")
	print("nbdocs:%s//size:%s" % (z.getNbDocs(),z.getVolumeDocs()))
		
		
if __name__== "__main__":
	
	ZeendocCheck()
	

	
	
