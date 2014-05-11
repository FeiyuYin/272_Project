from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.core.context_processors import csrf
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import models
from myapp.models import Server
from myapp.models import Webapp
from myapp.models import Source
from myapp.forms import SourceForm
from myapp.forms import WebappForm
from django.contrib.auth.decorators import login_required
from time import gmtime, strftime
import os

def index(request):
	if request.user.is_authenticated():
                username = request.user.username
		class_p = ''
                logio = 'Hi, ' + username + '. Click here to log out.'
                logiourl = '/accounts/logout/'
        else:
                logio = 'Hi, Click here to log in.'
                logiourl = '#modal1'
		class_p = 'modalLink'
	return render_to_response('index.html', {'logio':logio, 'logiourl':logiourl, 'class_p' : class_p})

def login(request):
	if request.user.is_authenticated():
		username = request.user.username
		class_p = ''
		logio = 'Hi, ' + username + '. Click here to log out.'
		logiourl = '/accounts/logout/'
		return render_to_response('login.html', {'logio':logio, 'logiourl':logiourl, 'class_p' : class_p})
	else:
		logio = 'Hi, Click here to log in.'
		logiourl = '#modal1'
		class_p = 'modalLink'
                return render_to_response('login.html', {'logio':logio, 'logiourl':logiourl, 'class_p' : class_p})

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
			class_p = ''
        	else:
			message = 'User is inactive!'
			logio = 'Hi, Click here to log in.'
                	logiourl = '#modal1'
			class_p = 'modalLink'
			
    	else:
		message = 'Authenticte failed!'
		logio = 'Hi, Click here to log in.'
                logiourl = '#modal1'
		class_p = 'modalLink'
	return render_to_response('show_message.html', {'message' : message, 'logio':logio, 'logiourl':logiourl, 'class_p': class_p})

def logout(request):
	auth.logout(request)
	logio = 'Hi, Click here to log in.'
        logiourl = '#modal1'
        class_p = 'modalLink'
	message = 'Logout Successfully'
	return render_to_response('show_message.html', {'message' : message ,'logio':logio, 'logiourl':logiourl, 'class_p' : class_p})

def register_start(request):
	if request.user.is_authenticated():
		message = 'You are already logged in!'
		logio = 'Hi, ' + username + '. Click here to log out.'
                logiourl = '/accounts/logout/'
		class_p = ''
		return render_to_response('show_message.html', {'message' : message, 'logio':logio, 'logiourl':logiourl, 'class_p' : class_p})
	else:
		form = UserCreationForm()
		logio = 'Hi, Click here to log in.'
                logiourl = '#modal1'
		class_p = 'modalLink'
		return render_to_response('register.html', {'form' : form, 'logio':logio, 'logiourl':logiourl, 'class_p' : class_p})

def register(request):
	form = UserCreationForm(request.POST)
	if form.is_valid():
		form.save()
		message = 'Register successful'
	else:
		message = 'Register failed'
	logio = 'Hi, Click here to log in.'
        logiourl = '/accounts/login/'
	logiourl = '#modal1'
        class_p = 'modalLink'
	return render_to_response('show_message.html', {'message' : message, 'logio':logio, 'logiourl':logiourl, 'class_p' : class_p})
	
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
			webapp.url = ""
			webapp.num_ver = 1
			webapp.save()
			form.save_m2m()

			source = Source()
                        source.name = str(webapp.name) + '_'  + str(webapp.id) + '_' + str(webapp.num_ver)
                        source.webapp = webapp
                        source.is_valid = True
                        source.s_file = webapp.source_file
                        source.description = webapp.description
                        source.save()			

			app_dir_name = str(webapp.name) + '_'  + str(webapp.id)
                        ver_dir_name = source.name
			uploaded_source_path = '/home/ubuntu/django_test/mysite/uploadedfile/' + str(webapp.source_file)
#			c_2 = 'mkdir -p /home/ubuntu/django_test/mysite/uploadedfile/' + app_dir_name + '/' + ver_dir_name
#			os.system(c_2)
			
#			c_3 = 'cp /home/ubuntu/django_test/mysite/uploadedfile/' + str(webapp.source_file) + ' /home/ubuntu/django_test/mysite/uploadedfile/' + app_dir_name + '/' + ver_dir_name
#			os.system(c_3)
			
#			c_1 = 'unzip ' + uploaded_source_path + ' -d /home/ubuntu/django_test/mysite/uploadedfile/'
#			os.system(c_1)

			c0 = 'sudo mkdir -p /srv/salt/172-31-38-144/' + app_dir_name + '/' + ver_dir_name
			os.system(c0)

			c1 = 'sudo cp ' + uploaded_source_path + ' ' + '/srv/salt/172-31-38-144/' + app_dir_name + '/' + ver_dir_name
			os.system(c1)
			
			c_2 = 'sudo unzip /srv/salt/172-31-38-144/' + app_dir_name + '/' + ver_dir_name + '/' + str(webapp.source_file) + ' -d /srv/salt/172-31-38-144/' + app_dir_name + '/' + ver_dir_name
			os.system(c_2)

			c_1 = 'sudo chown -R www-data:www-data /srv/salt/'
                        os.system(c_1)

			source_dir_path_minion = '/var/www/' + app_dir_name + '/' + ver_dir_name
			c_inner = "'mkdir -p " + source_dir_path_minion + "'"
			c2 = "sudo salt \"*\" cmd.run " + c_inner
			os.system(c2)


			sls_config = source_dir_path_minion + '/' + str(webapp.source_file) + ":\n file:\n  - managed\n  - source: salt://172-31-38-144/" + app_dir_name + '/' + ver_dir_name + '/' + str(webapp.source_file)
			
			with open("/srv/salt/172-31-38-144/init.sls", "a") as f:
			     f.write( "\n" + sls_config + "\n")			

			c4 = "sudo salt '*' state.highstate"
			os.system(c4)

			c5 = "sudo salt '*' cmd.run 'unzip /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + str(webapp.source_file) + " -d /var/www/" + app_dir_name + "/" + ver_dir_name + "'"
			os.system(c5)

			for pkg in webapp.package_needed.all():
                                package_shooter(pkg, webapp)

			os.system(c4)

#			webapp.url = 'http://54.186.171.250/' + app_dir_name + "/" + ver_dir_name + "/source/index.hmtml"
			c6 = "sudo salt '*' cmd.run 'nodejs /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/" + webapp.entry + "'"
			webapp.url = 'http://54.186.171.250:' + str(27202)
			webapp.save()

			message = 'Webapp created successfully.'
			return render_to_response('show_message.html', {'message': message, 'logio':logio, 'logiourl':logiourl})
		else:
			return render_to_response('deploy_new.html', {'form': form, 'logio':logio, 'logiourl':logiourl})

def package_shooter(pkg, wa):
	app_dir_name = str(wa.name) + '_'  + str(wa.id)
	ver_dir_name = str(wa.name) + '_'  + str(wa.id) + '_' + str(wa.num_ver)

	if pkg.name == 'npm':
                sls_config = pkg.name + ':\n pkg:\n  - installed'
        elif pkg.name == 'ejb' or pkg.name == 'express':
                sls_config = pkg.name + ':\n npm:\n  - installed\n  - dir: /var/www/' + app_dir_name + '/' + ver_dir_name + '/' + (str(wa.source_file).split('.zip')[0])

	for server in wa.server.all():
		dir_name = '/srv/salt/' + server.pr_ip + '/init.sls'
		with open(dir_name, "a") as f:
                             f.write( "\n" + sls_config + "\n")


@login_required
def upgrade_start(request, webapp_id):
	username = request.user.username
        logio = 'Hi, ' + username + '. Click here to log out.'
        logiourl = '/accounts/logout/'
	request.session['webapp_id'] = webapp_id 
        form = SourceForm()
        return render_to_response('upgrade.html', {'form': form, 'logio':logio, 'logiourl':logiourl})

@login_required
def upgrade(request, webapp_id):
	username = request.user.username
        logio = 'Hi, ' + username + '. Click here to log out.'
        logiourl = '/accounts/logout/'

	if request.method == 'POST':
		form = SourceForm(request.POST, request.FILES)	
		webapp = Webapp.objects.get(id = webapp_id)
		webapp.num_ver = webapp.num_ver + 1
		for s in webapp.source_set.all():
                        	s.is_valid = False
                        	s.save()

		if form.is_valid():
			source = form.save(commit = False)
			form.save_m2m()
 
			source.name = str(webapp.name) + '_'  + str(webapp.id) + '_' + str(webapp.num_ver)
			source.webapp = webapp
			source.is_valid = True
			source.save()
					
			webapp.source_file = source.s_file
			webapp.description = source.description
			app_dir_name = str(webapp.name) + '_'  + str(webapp.id)
        	        ver_dir_name = source.name
			uploaded_source_path = '/home/ubuntu/django_test/mysite/uploadedfile/' + str(webapp.source_file)

			webapp.url = 'http://54.186.171.250/' + app_dir_name + "/" + ver_dir_name + "/source/index.html"
			webapp.save()

			c0 = 'sudo mkdir -p /srv/salt/172-31-38-144/' + app_dir_name + '/' + ver_dir_name
                        os.system(c0)

                        c1 = 'sudo cp ' + uploaded_source_path + ' ' + '/srv/salt/172-31-38-144/' + app_dir_name + '/' + ver_dir_name
                        os.system(c1)

			c_2 = 'sudo unzip /srv/salt/172-31-38-144/' + app_dir_name + '/' + ver_dir_name + '/' + str(webapp.source_file) + ' -d /srv/salt/172-31-38-144/' + app_dir_name + '/' + ver_dir_name
                        os.system(c_2)

                        c_1 = 'sudo chown -R www-data:www-data /srv/salt/'
                        os.system(c_1)

                        source_dir_path_minion = '/var/www/' + app_dir_name + '/' + ver_dir_name
                        c_inner = "'mkdir -p " + source_dir_path_minion + "'"
                        c2 = "sudo salt \"*\" cmd.run " + c_inner
                        os.system(c2)


                        sls_config = source_dir_path_minion + '/' + str(webapp.source_file) + ":\n file:\n  - managed\n  - source: salt://172-31-38-144/" + app_dir_name + '/' + ver_dir_name + '/' + str(webapp.source_file)

                        with open("/srv/salt/172-31-38-144/init.sls", "a") as f:
                             f.write( "\n" + sls_config + "\n")

                        c4 = "sudo salt '*' state.highstate"
                        os.system(c4)

                        c5 = "sudo salt '*' cmd.run 'unzip /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + str(webapp.source_file) + " -d /var/www/" + app_dir_name + "/" + ver_dir_name + "'"
                        os.system(c5)

			message = "Upgrade Successfully."
		
			return render_to_response('show_message.html', {'message' : message, 'logio':logio, 'logiourl':logiourl})

	else:
		form = SourceForm()
	return render_to_response('upgrade.html', {'form': form, 'logio':logio, 'logiourl':logiourl})

@login_required
def view_versions(request, webapp_id):
	username = request.user.username
        logio = 'Hi, ' + username + '. Click here to log out.'
        logiourl = '/accounts/logout/'

	webapp = Webapp.objects.get(id = webapp_id)
	sources = []
	for s in webapp.source_set.all():
		if not s.is_valid:
			sources.append(s)
	
	return render_to_response('versions.html', {'sources': sources, 'logio':logio, 'logiourl':logiourl})

@login_required
def switch_to(request, source_id):
	username = request.user.username
        logio = 'Hi, ' + username + '. Click here to log out.'
        logiourl = '/accounts/logout/'

	source = Source.objects.get(id = source_id)
	webapp = source.webapp
	for s in webapp.source_set.all():
		s.is_valid = False
		s.save()
	source.is_valid = True
	source.save()
	webapp.source_file = source.s_file
	webapp.description = source.description

	app_dir_name = str(webapp.name) + '_'  + str(webapp.id)
        ver_dir_name = source.name
#	webapp.url = 'http://54.186.171.250/' + app_dir_name + "/" + ver_dir_name + "/source/index.html"
	webapp.save()

	return render_to_response('show_message.html', {'message' : 'Switch Successfully', 'logio':logio, 'logiourl':logiourl})

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
	form = SourceForm()
	return render_to_response('apps_new.html', {'logio':logio, 'logiourl':logiourl,'webapps': webapps, 'form': form})

@login_required
def displayapp(request, webapp_id ):
	username = request.user.username
        logio = 'Hi, ' + username + '. Click here to log out.'
        logiourl = '/accounts/logout/'
	
	webapp = Webapp.objects.get(id = webapp_id)
	for s in webapp.source_set.all():
		if s.is_valid == True:
			source = s
	app_dir_name = str(webapp.name) + '_'  + str(webapp.id)
        ver_dir_name = source.name
	path = '/srv/salt/172-31-38-144/' + app_dir_name + '/' + ver_dir_name

	data = []
	data.append(['Server', 'Load'])
	data.append(['S1', 100])
	data.append(['S2', 300])
	data.append(['S3', 200])

	return render_to_response('app_new.html', {'logio':logio, 'logiourl':logiourl, 'webapp': webapp, 'data' : data, 'path' : path})

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
