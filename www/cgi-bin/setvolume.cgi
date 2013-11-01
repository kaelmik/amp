#!/usr/bin/python

# Import modules for CGI handling 
import cgi, cgitb, alsaaudio


# Create instance of FieldStorage 
form = cgi.FieldStorage() 

# Get data from fields
volume = form.getvalue('volume')

mixer = alsaaudio.Mixer('Master')

t = int(volume)

mixer.setvolume(t)
