#!/usr/bin/python

# Import modules for CGI handling 
import cgi, cgitb, sys, os, commands, subprocess, string, fileinput, re, shutil

# Set current directory
from os import chdir
chdir("/usr/www-data/webconf/")

# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from fields

essid = form.getvalue('essid')
key  = form.getvalue('key')


if form.getvalue('dropdown'):
   subject = form.getvalue('dropdown')
else:
   subject = "Not entered"

# affiche repertoire courant
rep_cour = os.getcwd()

#WPA-PSK calcul de la cle wpa et ecriture du fichier interface(editface)

if subject == "WPA" :
	passcommand=("wpa_passphrase" + " " + essid + " " + key)
	u=commands.getoutput(passcommand) #wpa_passphrase command
	temp = re.search('(?<==)\w+', u) #extract psk after = 
	psk = temp.group(0) 
	s = open("ifacewpa").read()
	s = s.replace('wpassid', essid)
	s = s.replace('wpakey',psk)
	f = open('editface','w')
	f.write(s)
	f.close()

#WEP transfert les parametres au fichier interface(editface)

if subject == "WEP" :	
	s = open("ifacewep").read()
	s = s.replace('wepssid', essid)
	s = s.replace('wepkey',key)
	f = open('editface','w')
	f.write(s)
	f.close()

#Open transfer le nom du reseau au fichier interfaces(editface)

if subject == "Open" :
	s = open("ifaceopen").read()
	s = s.replace('openssid', essid)
	f = open('editface','w')
	f.write(s)
	f.close()

if subject == "Select" :
	print "Content-type:text/html\r\n\r\n"
	print "<html>"
	print "<head>"
	print "<title>Wifi Config - debarm</title>"
	print "<link rel='stylesheet' type='text/css' href='../style/style.css' />"
	print "</head>"
	print "<body>"
	print "<h3>Wrong parameters set</h3>"
	print "Please go back and choose encryption type!" 
	print "</body>"
	print "</html>"
else:
	shutil.copy('/etc/network/interfaces', '/etc/network/interfaces.bak') #make backup
	shutil.copy('editface', '/etc/network/interfaces') #write new interfaces

	print "Content-type:text/html\r\n\r\n"
	print "<html>"
	print "<head>"
	print "<title>Wifi Config - debarm</title>"
	print "<link rel='stylesheet' type='text/css' href='../style/style.css' />"
	print "</head>"
	print "<body>"
	print "<h3>Parameters successfully set</h3>"
	print "Selected encryption type is %s<br/></br> ESSID is <i>%s</i> and Key is <i>%s</i></br></br>" % (subject, essid, key)
	if subject == "WPA":
		print "Calculated PSK = <i>%s</i></br><br/>" % (psk)
	print "Restarting network can take a while and connexion will be lost after cliking <i>Restart Networking</i> button.</br></br>"
	print "Please reload home page in 1 minute after clicking button.</br></br>"
	print "<center><form action='/cgi-bin/wlan-restart.cgi' method='POST' target='hidden_frame'></br>"
	print "<input type='submit' value='Restart Networking...' /></center>"
	print "</body>"
	print "</html>"


