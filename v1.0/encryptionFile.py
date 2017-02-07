import os
import subprocess
import json


class encryption_file:

	def __init__(self, accounts_file, accounts_file_secure, gpg_userid, gpg_passphrase):
		self.accounts_file = accounts_file
		self.accounts_file_secure = accounts_file_secure
		self.user_id = gpg_userid
		self.passphrase = gpg_passphrase

	def encrypt_file(self):
		bashCommand = "gpg -e -r " + self.user_id + " " + self.accounts_file_secure

		FNULL = open(os.devnull, 'w')
		process = subprocess.check_output(bashCommand.split())

		os.remove(self.accounts_file_secure) 

		return process

	def decrypt_file(self):
		if( os.path.isfile(self.accounts_file_secure + ".gpg") != True ): raise IOError("No encrypted file")
		bashCommand = ["gpg", "--output" , self.accounts_file_secure, "--passphrase-fd" ,"0", "--batch" ,"--yes", "-d" , self.accounts_file_secure + ".gpg"]
		piped = ["echo" , self.passphrase]

		FNULL = open(os.devnull, 'w')
	
		out1 = subprocess.Popen(piped, stdout=subprocess.PIPE )
		out2 = subprocess.Popen(bashCommand, stdin=out1.stdout, stdout=FNULL, stderr=FNULL)
	
		output = out2.communicate()

		return output

	def getServices(self):
		return jsonToDict(self.accounts_file).keys()

	def mountFiles(self):
		accountBase = jsonToDict(self.accounts_file)
		decrypt_output = self.decrypt_file()
		accountBaseSecure = jsonToDict(self.accounts_file_secure)
		return accountBase, accountBaseSecure

	def unmountFiles(self,accountBase,accountBaseSecure):
		dictToJson(accountBase, self.accounts_file)
		dictToJson(accountBaseSecure, self.accounts_file_secure)

		encrypt_output = encrypt_file(account_base['gpg']['account'], accounts_file_encrypted)
		return None

	def getService(self,serviceName):
		if serviceName not in self.getServices():
			raise IOError("Not a valid service")

		accountBase, accountBaseSecure = self.mountFiles()
		myServiceOutput = accountBaseSecure[serviceName]

		self.unmountFiles(accountBase,accountBaseSecure)

		return myServiceOutput

	def addService(self, myService):
		if myService.serviceName in self.getServices():
			raise IOError("Reduntant service name")

		accountBase, accountBaseSecure = self.mountFiles()

		adding_dictionary = {'account': myService.accountName, 'other': myService.otherInfo}
		accountBase[myService.serviceName] = adding_dictionary
		accountBaseSecure[myService.serviceName] = adding_dictionary
		accountBaseSecure[myService.serviceName]['password']=self.accountPass

		self.unmountFiles(accountBase,accountBaseSecure)

		return True

	def removeService(self,myService):
		if myService.serviceName not in self.getServices():
			raise IOError("Reduntant service name")

		accountBase, accountBaseSecure = self.mountFiles()

		del accountBase[myService.serviceName]
		del accountBaseSecure[myService.serviceName]

		self.unmountFiles(accountBase,accountBaseSecure)

		return True


	def editService(self,myServiceName,newAccount='',newPass='',newOther=''):
		serviceToEdit = self.getService(myServiceName)
		if newAccount != '':
			serviceToEdit['account'] = newAccount
		if newPass != '':
			serviceToEdit['password'] = newPass
		if newOther != '':
			serviceToEdit['other'] = newOther

		self.removeService(serviceToEdit)
		self.addService(serviceToEdit)

		return True

def jsonToDict(jsonFile):
	with open(jsonFile,'r') as filename:
		outdict = json.load(filename)
	return outdict

def dictToJson(myDict,jsonFile):
	with open(jsonFile,'w') as filename:
		json.dump(myDict,filename)
	return None


class service: 

	def __init__(self, service_name, account_name ,account_pass, other_info=''):
		self.serviceName = service_name
		self.accountName = account_name
		self.accountPass = account_pass
		self.otherInfo = other_info

	#change 

