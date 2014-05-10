from django import forms
#from models import Document
from models import Webapp
from models import Language
from models import Package
from models import Server
from models import Source
from django.forms.extras.widgets import SelectDateWidget
from django.forms import ModelForm
from django.forms import CheckboxSelectMultiple

#class DocumentForm(forms.Form):
#	class Meta:
#		model = Document
#		fields = ('docfile')
#	docfile = forms.FileField(label='Select a file')

class SourceForm(ModelForm):
	class Meta:
		model = Source
		fields = ('s_file', 'description')

class WebappForm(ModelForm):
	language_needed = forms.ModelMultipleChoiceField(queryset=Language.objects.all(), widget=forms.CheckboxSelectMultiple(),required=True)
	package_needed = forms.ModelMultipleChoiceField(queryset=Package.objects.all(),widget=forms.CheckboxSelectMultiple(),required=True)
	server = forms.ModelMultipleChoiceField(queryset=Server.objects.all(),widget=forms.CheckboxSelectMultiple(),required=True)
	class Meta:
		model = Webapp
		fields = ('name', 'description', 'server', 'http_server', 'language_needed', 'package_needed', 'source_file', 'entry')
