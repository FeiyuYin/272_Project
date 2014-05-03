from django.db import models
from django.contrib.auth.models import User
from django.forms.extras.widgets import SelectDateWidget

class Document(models.Model):
	docfile = models.FileField(upload_to='documents/%Y/%m/%d')
	name  = models.CharField(max_length = 200)
	def __unicode__(self):
		return self.name

class Http_server(models.Model):
	name = models.CharField(max_length = 200)
        version = models.DecimalField(max_digits=6, decimal_places=3)
        def __unicode__(self):
                return self.name

class Language(models.Model):
	name = models.CharField(max_length = 200)
	version = models.DecimalField(max_digits=6, decimal_places=3)
	def __unicode__(self):
                return self.name

class Package(models.Model):
        name = models.CharField(max_length = 200)
        version = models.DecimalField(max_digits=6, decimal_places=3)
        def __unicode__(self):
                return self.name

class Server(models.Model):
	name = models.CharField(max_length = 200)
	os_type = models.CharField(max_length = 200)
	load = models.DecimalField(max_digits=6, decimal_places=3)
	def __unicode__(self):
                return self.name

class Webapp(models.Model):
	name = models.CharField(max_length = 200)
	description = models.TextField()
	user = models.ForeignKey(User)
	server = models.ManyToManyField(Server)
	http_server = models.ForeignKey(Http_server)
	language_needed = models.ManyToManyField(Language)
	package_needed = models.ManyToManyField(Package)
#	source_file = models.FileField(upload_to = 'sourcefiles/%Y/%m/%d')
	source_file = models.FileField(upload_to = '')
	create_date = models.DateTimeField(auto_now=False, auto_now_add=True)
	last_modify_date = models.DateTimeField(auto_now=True, auto_now_add=False)
	url = models.URLField()

#	source_file = models.OneToOneField(Document, blank=True)
	
	def __unicode__(self):
                 return self.name
