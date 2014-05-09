from django.contrib import admin
#from myapp.models import Document
from myapp.models import Server
from myapp.models import Webapp
from myapp.models import Http_server
from myapp.models import Language
from myapp.models import Package
from myapp.models import Source

#admin.site.register(Document)
admin.site.register(Server)
admin.site.register(Webapp)
admin.site.register(Http_server)
admin.site.register(Language)
admin.site.register(Package)
admin.site.register(Source)
