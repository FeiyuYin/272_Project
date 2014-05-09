from django import forms
from models import Document
from models import Webapp
from models import Language
from models import Package
from models import Server
from django.forms.extras.widgets import SelectDateWidget
from django.forms import ModelForm
from django.forms import CheckboxSelectMultiple

class DocumentForm(forms.Form):
	class Meta:
		model = Document
		fields = ('docfile')
	docfile = forms.FileField(label='Select a file')

#class SourceForm(forms.Form):
#        class Meta:
#                model = Source_file
#	fields = ('s_file')

class WebappForm(ModelForm):
	language_needed = forms.ModelMultipleChoiceField(queryset=Language.objects.all(), widget=forms.CheckboxSelectMultiple(),required=True)
	package_needed = forms.ModelMultipleChoiceField(queryset=Package.objects.all(),widget=forms.CheckboxSelectMultiple(),required=True)
	server = forms.ModelMultipleChoiceField(queryset=Server.objects.all(),widget=forms.CheckboxSelectMultiple(),required=True)
	class Meta:
		model = Webapp
		fields = ('name', 'description', 'server', 'http_server', 'language_needed', 'package_needed', 'source_file')
#		widgets = {
#			'language_needed' : CheckboxSelectMultiple(), 
#			'package_needed' : CheckboxSelectMultiple(), 
#			'server' : CheckboxSelectMultiple(), 
#		}
#	def save(self, commit = True):
#		username = request.user
#	name = forms.CharField(max_length = 200)
#	description = forms.CharField(widget=forms.Textarea)
#	server = forms.ChoiceField(widget = forms.Select, choices = SERVERS)
#	http_server = forms.ChoiceField(widget = forms.Select, choices = HTTPSERVERS)
#        language_needed = forms.MultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple, choices=LANGUAGES)
#	package_needed = forms.MultipleChoiceField(required=True, widget=forms.CheckboxSelectMultiple, choices=PACKAGES)
#        language_needed = forms.CharField(max_length = 200)
#        package_needed = forms.CharField(max_length = 200)
#        source_file = forms.FileField(widget=forms.FileInput)
