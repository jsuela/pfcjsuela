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
    url(r'^ranking/(?P<asign>.*)$', 'pfcapp.views.ranking', name='ranking'),
    url(r'^admin/', include(admin.site.urls)),
	url(r'^login', 'django.contrib.auth.views.login'),
	url(r'^logout', 'django.contrib.auth.views.logout'),
	url(r'^signin/profesor', 'pfcapp.views.signinprofesor', name='signinprofesor'),
	url(r'^signin', 'pfcapp.views.signin', name='signin'),
	url(r'^conf', 'pfcapp.views.conf', name='conf'),
	url(r'^contact', 'pfcapp.views.contact', name='contact'),
	url(r'^mispreguntas1', 'pfcapp.views.mispreguntas1', name='mispreguntas1'),
	url(r'^mispreguntas2', 'pfcapp.views.mispreguntas2', name='mispreguntas2'),
    url(r'^leccion/nueva', 'pfcapp.views.leccionnueva', name='leccionnueva'),
    url(r'^leccion/(?P<asign>.*)$', 'pfcapp.views.leccionporasignatura', name='leccionporasignatura'),
    url(r'^leccion', 'pfcapp.views.leccion', name='leccion'),
    url(r'^edita/(?P<user>.*)$', 'pfcapp.views.editausuario', name='editausuario'),
    url(r'^edita', 'pfcapp.views.edita', name='edita'),

    



	#url(r'^pruebagrafica', 'pfcapp.views.pruebagrafica', name='pruebagrafica'),
	url(r'^pruebagcm', 'pfcapp.views.pruebagcm', name='pruebagcm'),
    #graficando
    url(r'^grafica/aciertos/(?P<asign>.*)$', 'pfcapp.views.graficaaciertos', name='graficaaciertos'),
    url(r'^grafica/tipopreguntas/(?P<asign>.*)$', 'pfcapp.views.graficatipopreguntas', name='graficatipopreguntas'),
    url(r'^grafica/puntos', 'pfcapp.views.graficapuntosasign', name='graficapuntosasign'),
    url(r'^grafica/tiempo/(?P<user>.*)$', 'pfcapp.views.graficatiempousuario', name='graficatiempousuario'),
    url(r'^grafica/tiempo', 'pfcapp.views.graficatiempo', name='graficatiempo'),
    url(r'^grafica/(?P<asign>.*)$', 'pfcapp.views.graficaporasignatura', name='graficaporasignatura'),
    url(r'^grafica', 'pfcapp.views.grafica', name='grafica'),







	#android
    url(r'^android/clasificacion/(?P<usuario>.*)$', 'pfcapp.views.androidclasificacion', name='androidclasificacion'),
	url(r'^android/login', 'pfcapp.views.androidlogin', name='androidlogin'),
	url(r'^android/signin', 'pfcapp.views.androidsignin', name='androidsignin'),
	url(r'^android/enviarespuestas', 'pfcapp.views.androidenviarespuestas', name='androidenviarespuestas'),
	url(r'^android/sumapregunta/(?P<usuario>.*)$', 'pfcapp.views.androidsumapregunta', name='androidsumapregunta'),
	url(r'^android/sumatiempo/(?P<usuario>.*)$', 'pfcapp.views.androidsumatiempoocioso', name='androidsumatiempoocioso'),
	url(r'^android/preguntaextra/(?P<usuario>.*)$', 'pfcapp.views.androidpreguntaextra', name='androidpreguntaextra'),
	url(r'^android/pidepreguntas/(?P<usuario>.*)$', 'pfcapp.views.androidpidepreguntas', name='androidpidepreguntas'),
	url(r'^android/listacorrectas/(?P<usuario>.*)$', 'pfcapp.views.androidlistacorrectas', name='androidlistacorrectas'),

	url(r'^android/tips', 'pfcapp.views.androidtips', name='androidtips'),
	url(r'^android/enviapreguntaextra/(?P<emisor>.*)/(?P<receptor>.*)$', 'pfcapp.views.androidenviapreguntaextra', name='androidenviapreguntaextra'),
    url(r'^android/asignaturas/listado/completo/(?P<usuario>.*)$', 'pfcapp.views.androidasignaturascompleto', name='androidasignaturascompleto'),
    url(r'^android/asignaturas/listado/(?P<usuario>.*)$', 'pfcapp.views.androidasignaturasusuario', name='androidasignaturasusuario'),
    url(r'^android/asignaturas/matricula', 'pfcapp.views.androidasignaturasmatricula', name='androidasignaturasmatricula'),
    url(r'^android/colegios', 'pfcapp.views.androidcolegios', name='androidcolegios'),



	url(r'^android/gcm/registro', 'pfcapp.views.androidgcmregistrocliente', name='androidgcmregistrocliente'),





	url(r'^accounts/profile/','pfcapp.views.home', name='home'),
    url(r'^cses', 'pfcapp.views.cses', name='cses'),
    url(r'^imagen/(?P<path>.*)$', 'django.views.static.serve',
          {'document_root': './sfiles/imagen'}), 
    #descarga de la app
    url(r'^descarga/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './apps/preguntaras'}),

)
