import os
import subprocess

#Internal function - encrypts a file using GPG, deletes original file.
# returns bash output ??
def encrypt_file(user_id, location):

	if( os.path.isfile(location) != True ): raise IOError("file doesn't exist")

	if (os.path.isfile(location + '.gpg') ): os.remove(location + '.gpg')

	bashCommand = "gpg -e -r " + user_id + " " + location

	FNULL = open(os.devnull, 'w')
	process = subprocess.check_output(bashCommand.split())

	os.remove(location) 
	
	return process

#Internal function - decrypts a file using the affiliated passphrase, doesn't remove original file (to avoid having to re-encrypt for read-only cases) 
# returns bash output ??
def decrypt_file(passphrase, input_file, output_file):
	if( os.path.isfile(input_file) != True ): 
		raise IOError("File doesn't exist")

	bashCommand = ["gpg", "--output" , output_file , "--passphrase-fd" ,"0", "--batch" ,"--yes", "-d" , input_file]
	piped = ["echo" , passphrase]

	FNULL = open(os.devnull, 'w')
	
	out1 = subprocess.Popen(piped, stdout=subprocess.PIPE )
	out2 = subprocess.Popen(bashCommand, stdin=out1.stdout, stdout=FNULL, stderr=FNULL)
	
	output = out2.communicate()

	return output

#given the service name, returns all relevant information about the account, including the password.
#returns dictionary
def get_password_info(service_name,passphrase,directory=''):
	check_service_file = directory + 'account_base.json'
	file_with_pass = directory + 'account_base_secure.json.gpg'
	decryption_output = directory + 'account_base_secure.json'

	with open(check_service_file,'r') as checking:
		account_base = json.load(checking)

	flag = False
	if service_name in account_base.keys(): 
		flag = True

	if not flag: 
		raise IOError('No service with that name')
	else:
		check = decrypt_file(passphrase, file_with_pass, decryption_output)
		with open(decryption_output,'r') as checking2:
			account_base_secure = json.load(checking2)
		result = account_base_secure[service_name]

		os.remove(decryption_output)
		return result

#returns accounts in form of list
def get_account_list(directory=''):
	accounts_file = directory + 'account_base.json'
	with open(accounts_file,'r') as accounts: 
		account_base = json.load(accounts)
	account_list = account_base.keys() 
	return account_list 

#given service name, passphrase, optionally the account name, and optionally any other information
#returns boolean - indicating success of addition
def add_service_info(passphrase, service_name, account_name, account_pass, other_info, directory=''):
	accounts_file = directory + 'account_base.json'
	accounts_file_encrypted = directory + 'account_base_secure.json.gpg'
	accounts_file_decrypted = directory + 'account_base_secure.json'

	with open(accounts_file,'r') as accounts: 
		account_base = json.load(accounts)

	decrypt_output = decrypt_file(passphrase, accounts_file_encrypted, accounts_file_decrypted)
	with open(accounts_file_decrypted,'r') as accounts_secure:
		account_base_secure = json.load(accounts_secure)

	os.remove(accounts_file_decrypted)

	if service_name in account_base: raise IOError('Service name already exists')

	adding_dictionary = {'account': account_name, 'other': other_info}
	account_base[service_name] = adding_dictionary
	account_base_secure[service_name] = adding_dictionary
	account_base_secure[service_name]['password']=account_pass

	with open(accounts_file,'w') as account_write:
		json.dump(account_base, account_write)

	with open(accounts_file_decrypted,'w') as account_secure_write:
		json.dump(account_base_secure, account_secure_write)

	encrypt_output = encrypt_file(account_base['gpg']['account'], accounts_file_decrypted)

	return True	

#given an existing service name
#returns boolean, indicating whether or not the update procedure succeeded
def edit_service_info(passphrase,service_name,update_service_name='',update_account='',update_password='',update_other='', directory=''):
	accounts_file = directory + 'account_base.json'
	accounts_file_encrypted = directory + 'account_base_secure.json.gpg'
	accounts_file_decrypted = directory + 'account_base_secure.json'

	with open(accounts_file,'r') as accounts: 
		account_base = json.load(accounts)

	if service_name not in account_base: raise IOError('Service name does not exist')

	check = decrypt_file(passphrase, accounts_file_encrypted, accounts_file_decrypted)

	with open(accounts_file_decrypted,'r') as accounts_secure: 
		account_base_secure = json.load(accounts_secure)

	if update_service_name != '':
		account_base[update_service_name] = account_base[service_name]
		account_base_secure[update_service_name] = account_base_secure[service_name]
		del account_base[service_name]
		del account_base_secure[service_name]
		service_name = update_service_name

	if update_account != '':
		account_base[service_name]['account'] = update_account
		account_base_secure[service_name]['account'] = update_account

	if update_password != '':
		account_base_secure[service_name]['password'] = update_password

	if update_other != '':
		account_base[service_name]['other'] = update_other
		account_base_secure[service_name]['other'] = update_other

	with open(accounts_file,'w') as accounts:
		json.dump(account_base, accounts)

	with open(accounts_file_decrypted,'w') as accounts_secure:
		json.dump(account_base_secure,accounts_secure)

	check2 = encrypt_file(account_base['gpg']['account'],accounts_file_decrypted)

	return True

def remove_service(service_name,passphrase,directory=''):
	accounts_file = directory + 'account_base.json'
	accounts_file_encrypted = directory + 'account_base_secure.json.gpg'
	accounts_file_decrypted = directory + 'account_base_secure.json'

	with open(accounts_file,'r') as accounts: 
		account_base = json.load(accounts)

	if service_name not in account_base: raise IOError('Service name does not exist')

	check = decrypt_file(passphrase, accounts_file_encrypted, accounts_file_decrypted)

	with open(accounts_file_decrypted,'r') as accounts_secure: 
		account_base_secure = json.load(accounts_secure)

	del account_base[service_name]
	del account_base_secure[service_name]

	with open(accounts_file,'w') as accounts:
		json.dump(account_base, accounts)

	with open(accounts_file_decrypted,'w') as accounts_secure:
		json.dump(account_base_secure,accounts_secure)

	check2 = encrypt_file(account_base['gpg']['account'],accounts_file_decrypted)

	return True


#This function requires direct user interaction
#void - returns nothing (reconsider?)
def create_storage_file(gpg_account, gpg_other='', directory=''):
	accounts = {'gpg':{'account':gpg_account, 'other': gpg_other} }

	if os.path.exists(directory) and directory[len(directory)-1] != '/' : 
		raise IOError("Try again: provide a proper directory definition")

	if (os.path.isfile(directory + 'account_base.json') or os.path.isfile('account_base_secure.json')): 
		print "Account storage base already exists in this directory. Overwrite?"
		user_in = raw_input("Y/n:")
		if user_in.lower() =='y' : file_append = ''
		elif user_in.lower() =='n' : file_append = '_' + str( len(glob1('','account_base*') ) ) 
		else: print 'invalid input'
	else: file_append=''

	with open(directory + 'account_base' + file_append + '.json','w') as fp:
		json.dump(accounts, fp)

	print "New account storage base initiated. What's the password for the encryption key?"

	user_pass = getpass()

	accounts_secure = copy.deepcopy(accounts)
	accounts_secure['gpg']['password'] = user_pass

	secure_loc = directory + 'account_base' + file_append + '_secure.json'
	with open(secure_loc,'w') as fp:
		json.dump(accounts_secure, fp)

	#recall that encrypt_file deletes the original file 
	encrypt1 = encrypt_file(accounts['gpg']['account'], secure_loc)

	print "File created and encrypted in the specified location."

if __name__ == "__main__":
	import subprocess
	import os
	import json
	import copy
	import sys
	from getpass import getpass

	welcome_text = "Welcome to GPG-PWD."
	print welcome_text

	menu = {}
	menu['1'] = "Initialize Storage File"
	menu['2'] = "Retrieve a password"
	menu['3'] = "Display account list"
	menu['4'] = "Edit account info"
	menu['5'] = "Delete an account" 
	menu['6'] = "Add an account"
	menu['7'] = "Exit"

	while True:
		options = menu.keys()
		options.sort()
		print "Select an option:"
		for option in options:
			print option, menu[option]

		selected = raw_input("Choose one:")

		if selected == '1':
			gpg_account = raw_input("Please enter the account name which your GPG account is under: ")
			gpg_other = raw_input("Other gpg info? (hit enter to skip): ")
			directory = raw_input("Enter the directory for the storage files (default is current):")
			if os.path.exists(directory) != True and directory != '':
				print "Not a valid directory."
			elif directory == '':
				create_storage_file(gpg_account,gpg_other)
			else: 
				create_storage_file(gpg_account,gpg_other,directory=directory)

		elif selected == '2':
			service_name = raw_input("Please enter the service:")
			passphrase = getpass("Global encyrption passphrase:")
			count = 0
			while count < 3:
				try:
					infos = get_password_info(service_name,passphrase,directory='')
					print "\nService name: ", service_name
					print "Account name: ", infos['account']
					print "Password: ", infos['password']
					print "Other info: ", infos['other'], '\n'
					break
				except IOError:
					print "No service with the name "+service_name+". Please try again"
					count += 1

		elif selected == '3':
			try:
				listing = get_account_list()
				print "\n Accounts: \n"
				for l in listing: print '- ',l
				print('\n') 
			except IOError:
				print "Problem retrieving account list. Have you initialized the storage file?"

		elif selected == '4':
			passphrase = getpass("Global encryption passphrase:")
			service_name = raw_input("Please enter the service:")
			count = 0
			flag = False
			while count < 3:
				update_service = raw_input("Enter the new service name (or hit enter to leave it unchanged):")
				update_account = raw_input("Enter the new account name (or hit enter to leave it unchanged):")
				update_password = raw_input("Enter the new password (or hit enter to leave it unchanged):")
				update_other = raw_input("Enter any changes to the other info section:")

				print "Preparing to make the following changes..."
				if update_service != '': print "New service name: " + update_service
				if update_account != '': print "New account name: " + update_account
				if update_password != '': print "New password: " + update_password
				if update_other != '': print "New other info: " + update_other
				confirm = raw_input("Please confirm (y/n/q): ")

				if confirm.lower() == 'y':
					break
				elif confirm.lower() == 'n':
					print "OK, let's try again..."
				elif confirm.lower() == 'q':
					flag = True
				else:
					print "Unrecognized input"
					count += 1
			if flag: 
				print "Ok, quitting."
			elif not flag and count >= 3: 
				print "Please retry."
			else:
				try: 
					check = edit_service_info(passphrase,service_name,update_service_name=update_service,update_account=update_account,update_password=update_password,update_other=update_other, directory='')
					if check: 
						print "Sucessfully edited account info."
					else:
						print "Problem editing account info..."
				except IOError: 
					print "Service name does not exist."
				
		#delete an account
		elif selected == '5':
			service_name =raw_input("Enter the service you'd like to remove: ")
			passphrase = getpass("Global encryption passphrase:")
			last_chance = raw_input("Are you sure? (y/n): ")
			if last_chance.lower() == 'y':
				try: 
					check = remove_service(service_name, passphrase)
					if check:
						print "Service successfully removed.\n"
				except IOError:
					print "Service does not exist.\n"
			else: 
				print "OK. \n"
		#add ann account
		elif selected == '6':
			#print "Quit this prompt at anytime by pressing q.\n"
			confirm = 'n'
			while confirm.lower() == 'n' : 
				passphrase = getpass("Global encryption passphrase:")
				service_name = raw_input("First, give this service a name: ")
				account_name = raw_input("What's the account/email affilated with this service?: ")
				account_pass = raw_input("What's the password affiliated with this account?: ")
				other_info = raw_input("Any other info (security question answers, etc.): ")
				
				print "Preparing to add the following account info... \n"
				print "New service name: " + service_name
				print "New account name: " + account_name
				print "New password: " + account_pass
				print "New other info: " + other_info
				confirm = raw_input("Please confirm (y/n/q): ")

			if confirm.lower() == 'y':
				try: 
					check = add_service_info(passphrase, service_name, account_name, account_pass, other_info)
					if check: 
						print "Added service. \n"
					else:
						print "Problem adding service..." 
				except IOError:
					print "Problem completing request. Maybe incorrect passphrase?"

			elif confirm == 'q':
				print "Canceling...\n"
			else: 
				print "Invalid input.\n"

		elif selected == '7':
			choice = raw_input("Are you sure you'd like to exit? (Y/n)")
			if choice.lower() == 'y':
				print "Exiting now"
				sys.exit()
			elif choice.lower() == 'n': 
				pass
			else: 
				print "Unrecognized input"

		else: 
			print "Not an available option"




