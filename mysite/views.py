from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import models
from myapp.models import Document
from myapp.models import Server
from myapp.models import Webapp
from myapp.forms import DocumentForm
from myapp.forms import WebappForm
from django.contrib.auth.decorators import login_required
from time import gmtime, strftime
import cgi
import cgitb; cgitb.enable() 

#class Document(models.Model):
#    docfile = models.FileField(upload_to='documents/%Y/%m/%d')

#class DocumentForm(forms.Form):
#    docfile = forms.FileField(label='Select a file')

def index(request):
	if request.user.is_authenticated():
                username = request.user.username
                logio = 'Hi, ' + username + '. Click here to log out.'
                logiourl = '/accounts/logout/'
        else:
                logio = 'Hi, Click here to log in.'
                logiourl = '/accounts/login/'
	return render_to_response('index.html', {'logio':logio, 'logiourl':logiourl})

def login(request):
	if request.user.is_authenticated():
		username = request.user.username
		logio = 'Hi, ' + username + '. Click here to log out.'
		logiourl = '/accounts/logout/'
		return render_to_response('login.html', {'logio':logio, 'logiourl':logiourl})
	else:
		logio = 'Hi, Click here to log in.'
                logiourl = '/accounts/login/'
                return render_to_response('login.html', {'logio':logio, 'logiourl':logiourl})

def auth_view(request):
    	username = request.POST['user_name']
    	password = request.POST['user_password']
    	user = auth.authenticate(username=username, password=password)
    	if user is not None:
        	if user.is_active:
            		auth.login(request, user)
			message = 'Log in successfully'
			username = request.user.username
                	logio = 'Hi, ' + username + '. Click here to log out.'
                	logiourl = '/accounts/logout/'
        	else:
			message = 'User is inactive!'
			logio = 'Hi, Click here to log in.'
                	logiourl = '/accounts/login/'
    	else:
		message = 'Authenticte failed!'
		logio = 'Hi, Click here to log in.'
                logiourl = '/accounts/login/'
#	return render_to_response('cmp_auth.html', {'message' : message})
	return render_to_response('show_message.html', {'message' : message, 'logio':logio, 'logiourl':logiourl})

def logout(request):
	if request.user.is_authenticated():
		auth.logout(request)
		message = 'Log out successfully'
	else:
		message = 'You are not logged in!'
	logio = 'Hi, Click here to log in.'
        logiourl = '/accounts/login/'
	return render_to_response('show_message.html', {'message' : message, 'logio':logio, 'logiourl':logiourl})

def register_start(request):
	if request.user.is_authenticated():
		message = 'You are already logged in!'
		logio = 'Hi, ' + username + '. Click here to log out.'
                logiourl = '/accounts/logout/'
		return render_to_response('show_message.html', {'message' : message, 'logio':logio, 'logiourl':logiourl})
	else:
		form = UserCreationForm()
		logio = 'Hi, Click here to log in.'
                logiourl = '/accounts/login/'
		return render_to_response('register.html', {'form' : form, 'logio':logio, 'logiourl':logiourl})

def register(request):
	form = UserCreationForm(request.POST)
	if form.is_valid():
		form.save()
		message = 'Register successful'
	else:
		message = 'Register failed'
	logio = 'Hi, Click here to log in.'
        logiourl = '/accounts/login/'
	return render_to_response('show_message.html', {'message' : message, 'logio':logio, 'logiourl':logiourl})
	
@login_required
def deploy_start(request):
		username = request.user.username
                logio = 'Hi, ' + username + '. Click here to log out.'
                logiourl = '/accounts/logout/'
		form = WebappForm()
                return render_to_response('deploy_new.html', {'form': form, 'logio':logio, 'logiourl':logiourl})

@login_required
def deploy(request):
                username = request.user.username
                logio = 'Hi, ' + username + '. Click here to log out.'
                logiourl = '/accounts/logout/'
		form = WebappForm(request.POST, request.FILES)
		if form.is_valid():
			webapp = form.save(commit = False)
			webapp.user = request.user
			webapp.save()
			form.save_m2m()
			message = 'Webapp created successfully.'
			return render_to_response('show_message.html', {'message': message, 'logio':logio, 'logiourl':logiourl})
		else:
			return render_to_response('deploy_new.html', {'form': form, 'logio':logio, 'logiourl':logiourl})

@login_required
def displayapps(request):
	username = request.user.username
        logio = 'Hi, ' + username + '. Click here to log out.'
        logiourl = '/accounts/logout/'
	webapps = Webapp.objects.filter(user = request.user)
#	message = ''
#	for webapp in webapps:
#		for server in webapp.server.all():
#			message = message + server.name + ', '
	return render_to_response('apps.html', {'logio':logio, 'logiourl':logiourl,'webapps': webapps})

@login_required
def displayapp(request, webapp_id ):
	username = request.user.username
        logio = 'Hi, ' + username + '. Click here to log out.'
        logiourl = '/accounts/logout/'
	return render_to_response('app.html', {'logio':logio, 'logiourl':logiourl, 'webapp': Webapp.objects.get(id = webapp_id)})

def select(request):
	hs1 = 'Apache'
	hs2 = 'Tomcat'
	return render_to_response('select.html', {'hs1' : hs1, 'hs2' : hs2})

def display_session(request):
	hs = request.POST['httpserver']
	request.session['httpserver'] = hs
#	return render_to_response('show_message.html', {'message' : request.session['httpserver']})
	return render_to_response('show_message.html', {'message' : request.session['httpserver'], 'message2':request.session['member_id']})
	
def uploadfile_start(request):
	if request.user.is_authenticated():
		form = ModelFormWithFileField()
		return render_to_response('upload_file.html', {'form': form})
	else:
		return render_to_response('login.html')
		

def uploadfile(request):
	form = ModelFormWithFileField(request.POST, request.FILES)
	if form.is_valid():
#            handle_uploaded_file(request.FILES['file'])
		form.save()
		fn = request.FILES['file'].filename
		fp = '../uploadedfile/' + fn
		with open(fp, 'wb+') as destination:
        		for chunk in f.chunks():
            			destination.write(chunk)		
		return render_to_response('show_message.html',{'message' : 'File upload successful.'})
	else:
		return render_to_response('show_message.html',{'message' : 'File upload failed.'})
