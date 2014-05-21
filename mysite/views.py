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
import thread, time, socket, struct

#sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        		ver_dir_name = app_dir_name + '_' + str(webapp.num_ver)
			uploaded_source_path = '/home/ubuntu/django_test/mysite/uploadedfile/' + str(webapp.source_file)

			for s in webapp.server.all():
				config_dir(s, webapp)

			c1_5 = 'sudo rm ' + uploaded_source_path
			os.system(c1_5)

			c4 = "sudo salt '*' state.highstate"
			os.system(c4)

			for s in webapp.server.all():
				c5 = "sudo salt '" + s.salt_name + "' cmd.run 'unzip /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + str(webapp.source_file) + " -d /var/www/" + app_dir_name + "/" + ver_dir_name + "'"
				os.system(c5)

			for pkg in webapp.package_needed.all():
                               package_shooter(pkg, webapp)

			os.system(c4)
			
			for s in webapp.server.all():
				c5_1 = "sudo salt '" + s.salt_name + "' cmd.run 'cd /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/ ; npm install'" 
				os.system(c5_1)

			for s in webapp.server.all():
				c6 = "sudo salt '"+ s.salt_name +"' cmd.run 'cd /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/ ;nodejs " + webapp.entry + "'&"
				os.system(c6)

			webapp.url = 'http://54.187.149.192:' + str(27202)
			webapp.save()

			sock = init_socket()
			stat = {}
                        ips = get_server_ips(webapp)

                        data0 = ''
                        data0 = make_info(data0, 0, len(ips), ips, 27202)
                        sock.send(data0)

#			sock.shutdown(socket.SHUT_RDWR)
			sock.close()
			message = 'Webapp created successfully.'
			return render_to_response('show_message.html', {'message': message, 'logio':logio, 'logiourl':logiourl})
		else:
#			sock.close()
			return render_to_response('deploy_new.html', {'form': form, 'logio':logio, 'logiourl':logiourl})

def config_dir(s, webapp):
	sn = s.pr_ip
	app_dir_name = str(webapp.name) + '_'  + str(webapp.id)
        ver_dir_name = app_dir_name + '_' + str(webapp.num_ver)

	uploaded_source_path = '/home/ubuntu/django_test/mysite/uploadedfile/' + str(webapp.source_file)

	c0 = 'sudo mkdir -p /srv/salt/' + sn + '/' + app_dir_name + '/' + ver_dir_name
	os.system(c0)

	c1 = 'sudo cp ' + uploaded_source_path + ' /srv/salt/'+ sn + '/' + app_dir_name + '/' + ver_dir_name
	os.system(c1)
	
	c_2 = 'sudo unzip /srv/salt/' + sn + '/' + app_dir_name + '/' + ver_dir_name + '/' + str(webapp.source_file) + ' -d /srv/salt/' + sn + '/' + app_dir_name + '/' + ver_dir_name
	os.system(c_2)

	c_1 = 'sudo chown -R www-data:www-data /srv/salt/'
        os.system(c_1)

	source_dir_path_minion = '/var/www/' + app_dir_name + '/' + ver_dir_name
	c_inner = "'mkdir -p " + source_dir_path_minion + "'"
	c2 = "sudo salt '" + s.salt_name+ "' cmd.run " + c_inner
	os.system(c2)

	sls_config = source_dir_path_minion + '/' + str(webapp.source_file) + ":\n file:\n  - managed\n  - source: salt://" + sn + '/' + app_dir_name + '/' + ver_dir_name + '/' + str(webapp.source_file)
	sls_file_dir = "/srv/salt/" + sn + '/' + "init.sls"
			
	with open(sls_file_dir, "a") as f:
	     f.write( "\n" + sls_config + "\n")


def package_shooter(pkg, wa):
	app_dir_name = str(wa.name) + '_'  + str(wa.id)
	ver_dir_name = str(wa.name) + '_'  + str(wa.id) + '_' + str(wa.num_ver)

	sls_config = ''
	if pkg.name == 'npm':
                sls_config = pkg.name + ':\n pkg:\n  - installed'
        elif pkg.name == 'ejs' or pkg.name == 'express' or pkg.name == 'ejs' or pkg.name == 'mongoose' or pkg.name =='passport':
                sls_config = pkg.name + ':\n npm:\n  - installed\n  - dir: /var/www/' + app_dir_name + '/' + ver_dir_name + '/' + (str(wa.source_file).split('.zip')[0])
	

	for s in wa.server.all():
		dir_name = '/srv/salt/' + s.pr_ip + '/init.sls'
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
		for source in webapp.source_set.all():
                       	source.is_valid = False
                       	source.save()

		with open('/home/ubuntu/django_test/mysite/log', "a") as f:
			f.write( "\n" + 'Upgrade: Disable old source successrully.' + "\n")
			f.close()

		if form.is_valid():
			source = form.save(commit = False)
			form.save_m2m()
 
			source.name = str(webapp.name) + '_'  + str(webapp.id) + '_' + str(webapp.num_ver)
			source.webapp = webapp
			source.is_valid = True
			source.save()

			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                        	f.write( "\n" + 'Upgrade: New source saved in database.' + "\n")
                        	f.close()
					
			webapp.source_file = source.s_file
			webapp.description = source.description
			app_dir_name = str(webapp.name) + '_'  + str(webapp.id)
        	        ver_dir_name = source.name
			uploaded_source_path = '/home/ubuntu/django_test/mysite/uploadedfile/' + str(webapp.source_file)

#			webapp.url = 'http://54.186.171.250/' + app_dir_name + "/" + ver_dir_name + "/source/index.html"
			webapp.url = 'http://54.187.149.192:' + str(27202)
			webapp.save()

			for s in webapp.server.all():
				config_dir(s, webapp)
			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                        	f.write( "\n" + 'Upgrade: Config dirs for servers successrully.' + "\n")
                        	f.close()

			c1_5 = 'sudo rm ' + uploaded_source_path
                        os.system(c1_5)
			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                                f.write( "\n" + 'Upgrade: Clear uploaded file successrully.' + "\n")
                                f.close()

                        c4 = "sudo salt '*' state.highstate"
                        os.system(c4)
			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                                f.write( "\n" + 'Upgrade: Source file copy to Minions successrully.' + "\n")
                                f.close()

			for s in webapp.server.all():
                                c5 = "sudo salt '" + s.salt_name + "' cmd.run 'unzip /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + str(webapp.source_file) + " -d /var/www/" + app_dir_name + "/" + ver_dir_name + "'"
                                c5_1 = "sudo salt '" + s.salt_name + "' cmd.run 'cd /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/ ; npm install'"
                                os.system(c5)
                                os.system(c5_1)
			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                                f.write( "\n" + 'Upgrade: Unzip and install npm packages on Minions successrully.' + "\n")
                                f.close()

                        for pkg in webapp.package_needed.all():
                                package_shooter(pkg, webapp)

                        os.system(c4)
			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                                f.write( "\n" + 'Upgrade: Package installed on Minions successrully.' + "\n")
                                f.close()
			
			stat = {}
                        ips = get_server_ips(webapp)

			sock = init_socket()
			data0 = ''
			data0 = make_info(data0, 0, len(ips), ips, 27202)
			sock.send(data0)

			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
				f.write( "\n" + 'Upgrade: Send signal 0 successfully.' + "\n")

			data6 = ''
			data6 = make_info(data6, 6, len(ips), ips, 27202)
			sock.send(data6)

			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                                f.write( "\n" + 'Upgrade: Send signal 6 successfully.' + "\n")

			msg = sock.recv(2048)
			rev_info(msg, stat)

			sock.close()

			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                                f.write( "\n" + 'Upgrade: Receive info successfully.' + "\n" + str(stat) + '\n')

			for st in stat['ip_stat']:
				if st['load'] == 65523:
                  			s = Server.objects.get(pr_ip = st['ip'])
					c_kill = "sudo salt '"+ s.salt_name +"' cmd.run '/kill_nodejs'"
#					c_kill = "sudo salt '"+ s.salt_name +"' cmd.run 'kill -9 `ps -ef | grep server.js | awk '{print $2}'`'"
 	                                c_start = "sudo salt '"+ s.salt_name +"' cmd.run 'cd /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/ ;nodejs " + webapp.entry + "'&"

#					c_start = "sudo salt '"+ s.salt_name +"' cmd.run 'nodejs /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/" + webapp.entry + "'&"
					os.system(c_kill)
					os.system(c_start)
			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                                f.write( "\n" + 'Upgrade: Stop and start service on first part of Minions successrully.' + "\n")
                                f.close()
			
			sock = init_socket()
			data7 = ''
			stat = {}
                        data7 = make_info(data7, 7, len(ips), ips, 27202)
                        sock.send(data7)

			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                                f.write( "\n" + 'Upgrade: Send signal 7 successfully.' + "\n")

                        msg = sock.recv(2048)
                        rev_info(msg, stat)
			sock.close()

			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                                f.write( "\n" + 'Upgrade: Receive info successfully.' + "\n" + str(stat) + '\n')

                        for st in stat['ip_stat']:
                                if st['load'] == 65523:
                                        s = Server.objects.get(pr_ip = st['ip'])
					c_kill = "sudo salt '"+ s.salt_name +"' cmd.run '/kill_nodejs'"
#                                        c_kill = "sudo salt '"+ s.salt_name +"' cmd.run 'kill -9 `ps -ef | grep server.js | awk '{print $2}'`'"
					c_start = "sudo salt '"+ s.salt_name +"' cmd.run 'cd /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/ ;nodejs " + webapp.entry + "'&"
#					c_start = "sudo salt '"+ s.salt_name +"' cmd.run 'nodejs /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/" + webapp.entry + "'&"
                                        os.system(c_kill)
                                        os.system(c_start)
			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                                f.write( "\n" + 'Upgrade: Stop and start service on second part of Minions successrully.' + "\n")
                                f.close()

			sock = init_socket()
			data8 = ''
			data8 = make_info(data8, 8, len(ips), ips, 27202)
			sock.send(data8)

			with open('/home/ubuntu/django_test/mysite/log', "a") as f:
                                f.write( "\n" + 'Upgrade: Send signal 8 successfully.' + "\n")

#			sock.shutdown(socket.SHUT_RDWR)
			sock.close()
#                        for s in webapp.server.all():
#                               c6 = "sudo salt '"+ s.salt_name +"' cmd.run 'nodejs /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/" + webapp.entry + "'&"

			message = "Upgrade Successfully."
		
			return render_to_response('show_message.html', {'message' : message, 'logio':logio, 'logiourl':logiourl})

	else:
		form = SourceForm()
	return render_to_response('apps.html')

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

        stat = {}
        ips = get_server_ips(webapp)

	sock = init_socket()

	with open('/home/ubuntu/django_test/mysite/log', "a") as f:
             f.write( "\n" + 'Switch to: Socket init successfully.' + "\n")

        data0 = ''
        data0 = make_info(data0, 0, len(ips), ips, 27202)
        sock.send(data0)

	with open('/home/ubuntu/django_test/mysite/log', "a") as f:
             f.write( "\n" + 'Switch to: Send signal 0 successfully.' + "\n")

	data6 = ''
        data6 = make_info(data6, 6, len(ips), ips, 27202)
        sock.send(data6)

	with open('/home/ubuntu/django_test/mysite/log', "a") as f:
             f.write( "\n" + 'Switch to: Send signal 6 successfully.' + "\n")

        msg = sock.recv(2048)
        rev_info(msg, stat)

	sock.close()
	with open('/home/ubuntu/django_test/mysite/log', "a") as f:
             f.write( "\n" + 'Switch to: Receive info successfully.' + str(stat) + "\n")

        for st in stat['ip_stat']:
		if st['load'] == 65523:
                	s = Server.objects.get(pr_ip = st['ip'])
			c_kill = "sudo salt '"+ s.salt_name +"' cmd.run '/kill_nodejs'"
#                        c_kill = "sudo salt '"+ s.salt_name +"' cmd.run 'kill -9 `ps -ef | grep server.js | awk '{print $2}'`'"
			c_start = "sudo salt '"+ s.salt_name +"' cmd.run 'cd /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/ ;nodejs " + webapp.entry + "'&"
#                        c_start = "sudo salt '"+ s.salt_name +"' cmd.run 'nodejs /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/" + webapp.entry + "'&"
                        os.system(c_kill)
                        os.system(c_start)	

	sock = init_socket()
	stat = {}
	data7 = ''
        data7 = make_info(data7, 7, len(ips), ips, 27202)
        sock.send(data7)

	with open('/home/ubuntu/django_test/mysite/log', "a") as f:
             f.write( "\n" + 'Switch to: Send signal 7 successfully.' + "\n")

        msg = sock.recv(2048)
        rev_info(msg, stat)

	sock.close()
	with open('/home/ubuntu/django_test/mysite/log', "a") as f:
             f.write( "\n" + 'Switch to: Receive info successfully.' + str(stat) + "\n")

        for st in stat['ip_stat']:
        	if st['load'] == 65523:
                	s = Server.objects.get(pr_ip = st['ip'])
			c_kill = "sudo salt '"+ s.salt_name +"' cmd.run '/kill_nodejs'"
#                        c_kill = "sudo salt '"+ s.salt_name +"' cmd.run 'kill -9 `ps -ef | grep server.js | awk '{print $2}'`'"
			c_start = "sudo salt '"+ s.salt_name +"' cmd.run 'cd /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/ ;nodejs " + webapp.entry + "'&"
#                        c_start = "sudo salt '"+ s.salt_name +"' cmd.run 'nodejs /var/www/" + app_dir_name + "/" + ver_dir_name + "/" + (str(webapp.source_file).split('.zip')[0]) + "/" + webapp.entry + "'&"
                        os.system(c_kill)
                        os.system(c_start)

	sock = init_socket()
	data8 = ''
	data8 = make_info(data8, 8, len(ips), ips, 27202)
        sock.send(data8)

	with open('/home/ubuntu/django_test/mysite/log', "a") as f:
             f.write( "\n" + 'Switch to: Send signal 8 successfully.' + "\n")

#	sock.shutdown(socket.SHUT_RDWR)
	sock.close()
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
#	time.sleep(3)
	sock = init_socket()
	username = request.user.username
        logio = 'Hi, ' + username + '. Click here to log out.'
        logiourl = '/accounts/logout/'
	
	source = Source()
	webapp = Webapp.objects.get(id = webapp_id)
	for s in webapp.source_set.all():
		if s.is_valid == True:
			source = s
	app_dir_name = str(webapp.name) + '_'  + str(webapp.id)
        ver_dir_name = source.name

	ips = get_server_ips(webapp)
	
#	global sock
	data0 = ''
	data0 = make_info(data0, 0, len(ips), ips, 27202)
	sock.send(data0)

	with open('/home/ubuntu/django_test/mysite/log', "a") as f:
             f.write( "\n" + 'App detail: Send signal 0 successfully.' + "\n")

	stat = {}
	data5 = ''
	data5 = make_info(data5, 5, len(ips), ips, 27202)
	sock.send(data5)

#	with open('/home/ubuntu/django_test/mysite/log', "a") as f:
#             f.write( "\n" + 'App detail: Send signal 5 successfully.' + "\n")

	msg = sock.recv(2048)
	rev_info(msg, stat)

	with open('/home/ubuntu/django_test/mysite/log', "a") as f:
             f.write( "\n" + 'App detail: Receive info successfully.' + str(stat) + '\n')

	for st in stat['ip_stat']:	
		ser = Server.objects.get(pr_ip = st['ip'])
		if st['load'] == 0:
			ser.load = 100
		else:
			ser.load = st['load']
		if (st['load'] >> 24) == 1:
			ser.is_up = False
		else:
			ser.is_up = True
			


	server = webapp.server.all()[0]
	path = '/srv/salt/' + server.pr_ip + '/' + app_dir_name + '/' + ver_dir_name

	data = []
	data.append(['Server', 'Load'])

	for ser in webapp.server.all():
		if ser.is_up == True:
			data.append([str(ser.name), int(ser.load)])

#	sock.shutdown(socket.SHUT_RDWR)
        sock.close()

	return render_to_response('app_new.html', {'logio':logio, 'logiourl':logiourl, 'webapp': webapp, 'data' : data, 'path' : path})



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

def get_server_ips(webapp):
	ips = []
	for server in webapp.server.all():
		ips.append(server.pr_ip)
	return ips


def init_socket():
#    global sock
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
	sock.bind(('127.0.0.1', 35937))
	sock.connect(('127.0.0.1', 35938))
	return sock

def make_info(data, type, num, ips, port):
        data = data + struct.pack('II', type, num)
        for ip in ips:
                valP = 0
                ip_after = ip.split('-')
                for n in ip_after:
                        valP = valP << 8 | int(n)
                data = data + struct.pack('I', valP)
                data = data + struct.pack('II', port, 0)
        return data

def rev_info(msg, stat):
#        stat = {}
        type_, num = struct.unpack_from("II", msg, offset=0)
        stat['type'] = type_
        stat['num'] = num

        i = 0
        ip_stat = []
        while i < num:
                ip_raw = struct.unpack_from("I", msg, offset = 8 + i*12)[0]
                ip_hex_str = str(hex(ip_raw))
                ip = str(int(ip_hex_str[-8:-6], 16)) + '-' +str(int(ip_hex_str[-6:-4], 16)) + '-' +str(int(ip_hex_str[-4:-2], 16)) + '-' +str(int(ip_hex_str[-2:], 16))
                port = struct.unpack_from("I", msg, offset = 8 + i*12 + 4)[0]
                load = struct.unpack_from("I", msg, offset = 8 + i*12 + 8)[0]
                ip_stat.append({'ip': ip, 'port': port, 'load':load})
                i += 1

        stat['ip_stat'] = ip_stat
        print(stat)
        return stat

def info(request):
	return render_to_response('info.html')
