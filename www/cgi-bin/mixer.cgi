#!/usr/bin/python

# Import modules for CGI handling 
import cgi, cgitb, alsaaudio


# Create instance of FieldStorage 
form = cgi.FieldStorage() 

mute=form.getvalue('mute')
# Create Mixer instance
mixer = alsaaudio.Mixer('Output Mixer HiFi')

# Get data from fields

if form.getvalue('mute') == 'true' :
 mixer.setmute(1)
elif form.getvalue('mute') == 'mute' :
 mixer.setmute(1)

if form.getvalue('mute') == 'false' :
 mixer.setmute(0)
elif form.getvalue('mute') == None :
 mixer.setmute(0)
