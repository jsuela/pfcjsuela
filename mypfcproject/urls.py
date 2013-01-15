from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^$', 'pfcapp.views.home', name='home'),
    url(r'^home', 'pfcapp.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^login', 'django.contrib.auth.views.login'),
	url(r'^logout', 'django.contrib.auth.views.logout'),
	url(r'^signin/profesor', 'pfcapp.views.signinprofesor', name='signinprofesor'),
	url(r'^signin', 'pfcapp.views.signin', name='signin'),
	url(r'^conf', 'pfcapp.views.conf', name='conf'),
	url(r'^contact', 'pfcapp.views.contact', name='contact'),
	url(r'^mispreguntas1', 'pfcapp.views.mispreguntas1', name='mispreguntas1'),
	url(r'^mispreguntas2', 'pfcapp.views.mispreguntas2', name='mispreguntas2'),

	#android
	url(r'^android/login', 'pfcapp.views.androidlogin', name='androidlogin'),
	url(r'^android/enviarespuestas', 'pfcapp.views.androidenviarespuestas', name='androidenviarespuestas'),
	url(r'^android/sumapregunta/(?P<usuario>.*)$', 'pfcapp.views.androidsumapregunta', name='androidsumapregunta'),
	url(r'^android/pidepreguntas/(?P<usuario>.*)$', 'pfcapp.views.androidpidepreguntas', name='androidpidepreguntas'),
	url(r'^android/listacorrectas/(?P<usuario>.*)$', 'pfcapp.views.androidlistacorrectas', name='androidlistacorrectas'),
	url(r'^android/clasificacion', 'pfcapp.views.androidclasificacion', name='androidclasificacion'),


	url(r'^accounts/profile/','pfcapp.views.home', name='home'),
    url(r'^cses', 'pfcapp.views.cses', name='cses'),
    (r'^imagen/(?P<path>.*)$', 'django.views.static.serve',
          {'document_root': './sfiles/imagen'}), 

)
