from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

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
    url(r'^$', 'project2.views.index'),
    url(r'^project1/', 'project1.views.index' ),
    url(r'^project2/', 'project2.views.index' ),
    url(r'^build_index/', 'project2.views.build_index' ),
    url(r'^pubmed/', 'pubmed_fetcher.views.index' ),
    url(r'^load/', 'pubmed_fetcher.views.load_articles' ),
    url(r'^bigtxt/', 'pubmed_fetcher.views.bigtxt_generator' ),
    url(r'^train/', 'project2.views.train_spelling_corrector' ),
	#(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT, 'show_indexes': True}),
)


urlpatterns += staticfiles_urlpatterns()