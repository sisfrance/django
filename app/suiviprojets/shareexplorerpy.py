import sharepy as share
import json

URL='https://sisfranceeu0.sharepoint.com'
USER_NAME='connect@sisfranceeu0.onmicrosoft.com'
PASSWD='C0n33!#Mt'    


class SharePointExplorer:
	
	def __init__(self,site):
		self.session=self.connecting()
		self.site=site
		self.result=[]

	def connecting(self):
		try:
			return share.connect(URL,USER_NAME,PASSWD)
		except Exception as error:
			print(error)
	
	def liste_files(self):
		response=self.session.get(URL+"/sites/"+self.site+"/_api/web/lists/getbytitle('Documents')/items?$select=FileLeafRef,FileRef&top=30")
		result=json.loads(response.text)
		self.result=result
		return [f["FileLeafRef"] for f in dict(result)['d']['results']]
		
	def liste_dir(self,partage="documents%20partages"):
		response=self.session.get(URL+"/sites/"+self.site+"/_api/web/lists/GetByTitle('Documents')/items?$filter=ContentType eq 'Folder'")
		result=json.loads(response.text)
		self.result=result
		return result
	

	def upload_files(self):
		headers = {"accept": "application/json;odata=verbose",
		"content-type": "application/x-www-urlencoded; charset=UTF-8"}
		fileToUpload = "/var/app/suiviprojets/suiviprojets/media/tmp"
		filename="toto1.txt"
		with open(fileToUpload+"/"+filename, 'rb') as read_file:
			content = read_file.read()
			print(content)
			url=URL+"/_api/web/getfolderbyserverrelativeurl('/sites/"+self.site+"/')/Files/add(url='"+filename+"',overwrite=true)"
			print(url)
			p = self.session.post(url, data=content, headers=headers)
			"""p =zeen.session.post("https://sisfranceeu0.sharepoint.com/sites/Zeendoc/_api/web/GetFoldersByServerRelativeUrl('/sites/Zeendoc/documents%20partages/')/Files/add(url='toto.txt',overwrite=true)",data=content,headers=headers)"""

if __name__=="__main__":
	cd=SharePointExplorer('Zeendoc')
	print(cd.liste_files())
	print(cd.liste_dir())
	cd.upload_files()
	
