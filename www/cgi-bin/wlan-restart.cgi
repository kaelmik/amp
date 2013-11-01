#!/usr/bin/python

# Import modules for CGI handling 
import cgi, cgitb, sys, os, commands, subprocess, string, fileinput, re, shutil



subprocess.call(["sudo", "/usr/bin/wifirestart.sh"])