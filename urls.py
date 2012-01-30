from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'irsite.views.home', name='home'),
    # url(r'^irsite/', include('irsite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^project1/', 'project1.views.index' ),
	url(r'^/$', 'project1.views.index', name='index'),
	(r'^static/(?P<path>.*)$', 'django.views.static.serve',
	        {'document_root': '/Users/jeroyang/Dropbox/irsite/static/', 'show_indexes': True}),
)
