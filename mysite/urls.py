from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	
	url(r'^index/$', 'mysite.views.index'),
	url(r'^accounts/login/$', 'mysite.views.login'),
	url(r'^accounts/auth/$', 'mysite.views.auth_view'),
	url(r'^accounts/logout/$', 'mysite.views.logout'),
	url(r'^accounts/register_start/$', 'mysite.views.register_start'),
	url(r'^accounts/register/$', 'mysite.views.register'),
	url(r'^features/deploy_start/$', 'mysite.views.deploy_start'),
	url(r'^features/deploy/$', 'mysite.views.deploy'),
	url(r'^features/displayapps/$', 'mysite.views.displayapps'),
	url(r'^features/displayapp/get/(?P<webapp_id>\d+)/$', 'mysite.views.displayapp'),
	url(r'^features/upgrade_start/get/(?P<webapp_id>\d+)/$', 'mysite.views.upgrade_start'),
	url(r'^features/upgrade/', 'mysite.views.upgrade'),
	url(r'^features/view_versions/get/(?P<webapp_id>\d+)/$', 'mysite.views.view_versions'),
	url(r'^features/switch_to/get/(?P<source_id>\d+)/$', 'mysite.views.switch_to'),
#	url(r'^test/select/$', 'mysite.views.select'),
#	url(r'^test/displaysession/$', 'mysite.views.display_session'),
#	url(r'^features/uploadfile_start/$', 'mysite.views.uploadfile_start'),
#	url(r'^features/uploadfile/$', 'mysite.views.uploadfile'),
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)
