# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound, HttpRequest, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from pfcapp.models import PreguntasPendientes, PreguntasCompletas, PreguntasRespondidas, Puntuaciones, PreguntasVisibles, Tips, CodigosGCM, Asignaturas, AsignaturasAlumno, Colegios, Persona, MedidaOcioDiaria
from django.core.context_processors import csrf
from django.contrib.auth import authenticate

from django.template.loader import get_template
from django.template import Context, RequestContext

from django.utils import simplejson
from django.core import serializers

from datetime import datetime, date

import httplib, urllib

from django.utils.encoding import smart_str

#-------------------------------------------------------------------------------
#mostraremos el ranking (profesor) o listado de asignaturas
#-------------------------------------------------------------------------------

def home(request):

	template = get_template("registration/inicioautes.html")
	if request.user.is_authenticated():
		usuario=request.user.username
		if request.method=='GET':
			ranking=Puntuaciones.objects.all()
			ranking=ranking.extra(order_by = ['-puntos'])


			if request.user.is_staff:
				profesor=usuario

				#para que muestre la asignatura que imparte
				a=Asignaturas.objects.get(profesor=profesor)
				asignatura=a.asignatura
				#y filtro para que solo aparezcan sus alumnos
				ranking= ranking.extra(where=['asignatura=%s'], params=[asignatura])
				#y filtro para que sean solo los de su colegio ya que puede haber dos asignaturas con elmismo nombre
				#en distrintos colegios
				u = User.objects.get(username=usuario)
				usuario_colegio = u.persona.colegio
				
				ranking= ranking.extra(where=['colegio=%s'], params=[usuario_colegio])
				
				listaAsignaturas=''
			#si es alumno
			else:
				#le envio el listado de sus asignaturas matriculadas para que elija cual ranking quiere
				listaAsignaturas = AsignaturasAlumno.objects.filter(usuario=usuario)
				profesor=''
				asignatura=''
				ranking=''
			return HttpResponse(template.render(Context({'user':usuario,'profesor':profesor,'asignatura':asignatura,'ranking':ranking, 'listaAsignaturas':listaAsignaturas})))
	else:
		return HttpResponseRedirect('/login')


#-------------------------------------------------------------------------------
#mostraremos el ranking de la asignatura dada
#-------------------------------------------------------------------------------

def ranking(request, asign):

	if request.user.is_authenticated():
		usuario=request.user.username
		if request.method=='GET':
			if request.user.is_staff:
				return HttpResponseRedirect('/home')
			else:
				
				profesor=''
				asignatura=asign
				listaAsignaturas=''
				#devuelvo el ranking de esa asignatura, para ello obtengo si el usuario verdaderamente esta matriculado y no cotillea

				existeMatr = AsignaturasAlumno.objects.filter(usuario=usuario)
				existeMatr = existeMatr.extra(where=['asignatura=%s'], params=[asign])
				
				#como la asignatura puede tener el mismo nombre en dos colegios distintos, le tengo que pasar el colegio
				#para ello, extraigo el colegio del usuario
				u = User.objects.get(username=usuario)
				usuario_colegio = u.persona.colegio
				
				ranking=Puntuaciones.objects.all()
				ranking=ranking.extra(order_by = ['-puntos'])
				ranking= ranking.extra(where=['asignatura=%s'], params=[asign])
				#filtro también por colegio por si hubiese la misma asignatura en colegios distintos
				ranking= ranking.extra(where=['colegio=%s'], params=[usuario_colegio])

				return render_to_response('registration/inicioautes.html', {'user':usuario,'profesor':profesor,'asignatura':asignatura,'ranking':ranking, 'listaAsignaturas':listaAsignaturas}, context_instance=RequestContext(request))			
				

	else:
		return HttpResponseRedirect('/login')


#-------------------------------------------------------------------------------
#mostraremos la info de contacto
#-------------------------------------------------------------------------------

def contact(request):

	if request.user.is_authenticated():
		template = get_template("registration/contact.html")
		usuario=request.user.username
		if request.method=='GET':
			if request.user.is_staff:
				profesor=usuario
			else:
				profesor=''
			return HttpResponse(template.render(Context({'user':usuario,'profesor':profesor,'body':""})))
	else:
		return HttpResponseRedirect('/login')

#-------------------------------------------------------------------------------
#devuelve el css
#-------------------------------------------------------------------------------

def cses(request):
	fichero=open('style.css')
	cssestandar=fichero.read()	
	myResponse = HttpResponse(cssestandar)
	myResponse['Content-Type'] = 'text/css'
	return myResponse

#-------------------------------------------------------------------------------
#Registro de alumnos
#-------------------------------------------------------------------------------

def signin(request):
	#csrftoken
	c={}
	c.update(csrf(request))

	if request.user.is_authenticated():
		return HttpResponseRedirect('/home')
	else:
		if request.method == "POST":
			colegio=request.POST['colegio']
			print colegio
			username=request.POST['user']
			
			if " " in username:
				signFail= "Error! El nombre de usuario no puede contener espacios"
				return render_to_response('registration/signin.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
			
			if username=="":
				signFail= "Error! Debes rellenar todos los campos"
				return render_to_response('registration/signin.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
			else:
				try:
					u = User.objects.get(username__exact=username)
					if str(u) == str(username):
						signFail= "¡Error! El usuario "+username +" ya existe, pruebe de nuevo con otro usuario"
						return render_to_response('registration/signin.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
				except User.DoesNotExist:
					password=request.POST['password']
					password2=request.POST['password2']
					colegio=request.POST['colegio']

					email=request.POST['email']
					if (password=="") or (email==""):
						signFail= "¡Error! Debes rellenar todos los campos"
						return render_to_response('registration/signin.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
					elif (len(password)<6):
						signFail= "¡Error! La contraseña debe ser de al menos 6 caracteres"
						return render_to_response('registration/signin.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
					elif (password2!=password):
						signFail= "¡Error! Los campos de la contraseña deben coincidir"
						return render_to_response('registration/signin.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
					elif (colegio=="Elija Colegio"):
						signFail= "¡Error! Debes seleccionar tu colegio"
						return render_to_response('registration/signin.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
					else:
						user = User.objects.create_user(username,email,password)
						user.save()
						
						record1=Persona(usuario=user, colegio=colegio)
						record1.save()	
						
############################################################################################################################################################################################
#hecho en matricular asignatura						#añadimos a la tabla de puntuaciones
						#puntuaciones= Puntuaciones(usuario=username, puntos=0, preguntaextra=0, preguntaobligada=0, preguntarecibidaamistosa=0, preguntaenviadaamistosa=0);
						#puntuaciones.save()

						#añadimos las preguntas existentes al nuevo usuario para que disponga de todas
						#listadopreguntas= PreguntasCompletas.objects.all()
						#for i in listadopreguntas:
						#	usuario_pendiente = username
						#	pregunta= i.pregunta
						#	respuesta= i.respuesta
						#	respuesta2= i.respuesta2
						#	respuesta3= i.respuesta3
						#	record=PreguntasPendientes(usuario_pendiente=usuario_pendiente,pregunta=pregunta,respuesta=respuesta,respuesta2=respuesta2, respuesta3=respuesta3)
						#	record.save()
############################################################################################################################################################################################							

						sign = "Tu registro se ha realizado con éxito, ya puedes iniciar sesión también en la aplicación móvil"
						return render_to_response('registration/signin.html', {'user':username,'exito':sign}, context_instance=RequestContext(request))
		elif request.method == "GET":
			lcolegios=Colegios.objects.all()
			lcolegios=lcolegios.extra(order_by = ['colegio'])
			return render_to_response('registration/signin.html', {'user':'', 'lcolegios':lcolegios}, context_instance=RequestContext(request))
		
		else:
			return render_to_response('registration/signin.html',c)

#-------------------------------------------------------------------------------
#Registro de profesores
#-------------------------------------------------------------------------------

def signinprofesor(request):
	#csrftoken
	c={}
	c.update(csrf(request))

	if request.user.is_authenticated():
		return HttpResponseRedirect('/home')
	else:
		#GET
		if request.method == "GET":
			lcolegios=Colegios.objects.all()
			lcolegios=lcolegios.extra(order_by = ['colegio'])
			return render_to_response('registration/signinprofesor.html', {'user':'', 'lcolegios':lcolegios}, context_instance=RequestContext(request))
		if request.method == "POST":
			CLAVE_ADMIN="efsmcegqempsecelmcemqeg"
			clave=request.POST['clave']
			if CLAVE_ADMIN == clave:

				username=request.POST['user']
				colegioAlta=request.POST['colegioAlta']
				colegio=request.POST['colegio']
				if ((username=="") or ((colegio=="Elija Colegio") and (colegioAlta==""))):
					signFail= "¡Error! Debes rellenar todos los campos"
					return render_to_response('registration/signinprofesor.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
				else:
					try:
						u = User.objects.get(username__exact=username)
						if str(u) == str(username):
							signFail= "Error! El usuario "+username +" ya existe, pruebe de nuevo con otro usuario"
							return render_to_response('registration/signinprofesor.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
					except User.DoesNotExist:
						password=request.POST['password']
						password2=request.POST['password2']
						asignatura=request.POST['asignatura']
						
						#comprobamos si ya existe alguna asignatura identica
						try:
							if (colegio=="Elija Colegio"):
								asig = Asignaturas.objects.get(asignatura=asignatura, colegio=colegioAlta)
								signFail= "¡Error! La asignatura ya existe"
							else:
								asig = Asignaturas.objects.get(asignatura=asignatura, colegio=colegio)
								signFail= "¡Error! La asignatura ya existe"
								

							if (colegio=="Elija Colegio"):
								asig = Colegios.objects.get(colegio=colegioAlta)
								signFail= "¡Error! El colegio ya existe"
									
							return render_to_response('registration/signinprofesor.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
						except Asignaturas.DoesNotExist, Colegios.DoesNotExist:


							email=request.POST['email']
							if (password=="") or (email==""):
								signFail= "¡Error! Debes rellenar todos los campos"
								return render_to_response('registration/signinprofesor.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
							elif (len(password)<6):
								signFail= "¡Error! La contraseña debe ser de al menos 6 caracteres"
								return render_to_response('registration/signinprofesor.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
							elif (password2!=password):
								signFail= "¡Error! Los campos de la contraseña deben coincidir"
								return render_to_response('registration/signinprofesor.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
							elif ((colegio!="Elija Colegio") and (colegioAlta!="")):
								signFail= "¡Error! No puedes seleccionar dos colegios"
								return render_to_response('registration/signinprofesor.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
							else:
								
								user = User.objects.create_user(username,email,password)
								# staff solo para el profesor
								user.is_staff = True
								user.save()
								#almaceno el cole al que pertenece
								if (colegio=="Elija Colegio"):
									record1=Persona(usuario=user, colegio=colegioAlta)
									
								else:
									record1=Persona(usuario=user, colegio=colegio)
								record1.save()	
								
								#miro si es un colegio nuevo o ya existía, si colegio esta en blanco , sino no almacena
								if (colegio=="Elija Colegio"):
									record2=Colegios(colegio=colegioAlta)
									record2.save()								
																			
														
								
								#almaceno también la asignatura que imparte dicho profesor
								if (colegio=="Elija Colegio"):
									record=Asignaturas(asignatura=asignatura,profesor=username, colegio=colegioAlta)
								else:
									record=Asignaturas(asignatura=asignatura,profesor=username, colegio=colegio)								
								record.save()
								sign = "Tu registro se ha realizado con éxito"
								return render_to_response('registration/signinprofesor.html', {'user':username,'exito':sign}, context_instance=RequestContext(request))
			#si la clave admin no coincide
			else:
				signFail= "¡Error! Introduce correctamente la clave dada por el administrador"
				return render_to_response('registration/signinprofesor.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
		#si no es ni GET ni POST
		else:
			return HttpResponseRedirect('/login')

#-------------------------------------------------------------------------------
#Si es alumno devuelve las preguntas que tiene pendientes
#si es profesor formulario para añadir preguntas
#-------------------------------------------------------------------------------

def mispreguntas1(request):
	#csrftoken
	c={}
	c.update(csrf(request))
	if request.user.is_authenticated():
		template = get_template("registration/formulario1.html")
		usuario=request.user.username
		#si es staff
		if request.user.is_staff:
			#si es profesor mostrará el formulario
			if request.method=='GET':
				return render_to_response('registration/formulario1.html', {'profesor':usuario}, context_instance=RequestContext(request))
			if request.method == "POST":
				pregunta=request.POST['pregunta']
				respuesta=request.POST['respuesta']
				respuesta1_correcta=request.POST['respuesta1_correcta']
				respuesta2=request.POST['respuesta2']
				respuesta2_correcta=request.POST['respuesta2_correcta']
				respuesta3=request.POST['respuesta3']
				respuesta3_correcta=request.POST['respuesta3_correcta']

				if (respuesta3_correcta=="true") and (respuesta2_correcta=="true") and (respuesta3_correcta=="true"):
					formFail= "Error! Solo puede existir una opción correcta"
					return render_to_response('registration/formulario1.html', {'profesor':usuario,'error':formFail}, context_instance=RequestContext(request))
				elif (((respuesta1_correcta=="true") and (respuesta2_correcta=="true")) or ((respuesta1_correcta=="true") and (respuesta3_correcta=="true")) or ((respuesta2_correcta=="true") and (respuesta3_correcta=="true"))):
					formFail= "Error! Solo debe existir una opción correcta"
					return render_to_response('registration/formulario1.html', {'profesor':usuario,'error':formFail}, context_instance=RequestContext(request))
				elif ((respuesta3_correcta=="false") and (respuesta2_correcta=="false") and (respuesta1_correcta=="false")):
					formFail= "Error! Debe existir una opción correcta"
					return render_to_response('registration/formulario1.html', {'profesor':usuario,'error':formFail}, context_instance=RequestContext(request))
				elif ((respuesta=='') or (respuesta2=='') or (respuesta3=='')):
					formFail= "Error! Rellena todos los campos"
					return render_to_response('registration/formulario1.html', {'profesor':usuario,'error':formFail}, context_instance=RequestContext(request))
				else:

					

					Usuarios= User.objects.all()
					

					#compruebo si ya esxitia la pregunta, si exsitia doy error, si no, almaceno
					try:
						#miro la asignatura del profesor
						usuario=request.user.username
						#miro el colegio del profesor para poder filtrar tb por colegio
						miusuario = User.objects.get(username=usuario)
						usuario_colegio = miusuario.persona.colegio
												
						u=Asignaturas.objects.get(profesor=usuario, colegio=usuario_colegio)
						asignatura = u.asignatura
						pexiste=PreguntasCompletas.objects.get(pregunta=pregunta, asignatura=asignatura, colegio=usuario_colegio)
						#if (str(pexiste.pregunta)!=str("")):
					except PreguntasCompletas.DoesNotExist:
						#miro la asignatura del profesor
						usuario=request.user.username
						#miro el colegio del profesor para poder filtrar tb por colegio
						miusuario = User.objects.get(username=usuario)
						usuario_colegio = miusuario.persona.colegio
						
						u=Asignaturas.objects.get(profesor=usuario, colegio=usuario_colegio)
						asignatura = u.asignatura

						#almaceno
						record=PreguntasCompletas(pregunta=pregunta,respuesta=respuesta,respuesta1_correcta=respuesta1_correcta ,respuesta2=respuesta2,respuesta2_correcta=respuesta2_correcta, respuesta3=respuesta3,respuesta3_correcta=respuesta3_correcta, asignatura=asignatura, colegio=usuario_colegio)
						record.save()
						for i in Usuarios:
							if not (i.is_staff):
								usuario_pendiente = i.username
					
								record2=PreguntasPendientes(usuario_pendiente=usuario_pendiente,pregunta=pregunta,respuesta=respuesta,respuesta2=respuesta2, respuesta3=respuesta3, asignatura=asignatura)
								record2.save()

						form = "Tu pregunta se ha almacenado."
						return render_to_response('registration/formulario1.html', {'profesor':usuario,'exito':form}, context_instance=RequestContext(request)) 

					#si ya se habia alamacenado la pregunta anteriormente aviso del error
					formFail= "Error! La pregunta ya existe"
					return render_to_response('registration/formulario1.html', {'profesor':usuario,'error':formFail}, context_instance=RequestContext(request))




   
			#si no es ni GET ni POST
			else:
				return render_to_response('registration/formulario1.html', {'profesor':usuario,'error':"Error"}, context_instance=RequestContext(request))
		#si es alumno
		else:
			try:
				pvisibles=PreguntasVisibles.objects.filter(usuario_pendiente=usuario)
			except PreguntasVisibles.DoesNotExist:
				pvisibles=''
			return render_to_response('registration/formulario1.html', {'alumno':usuario,'listadopendientes':pvisibles}, context_instance=RequestContext(request))   
	#si no esta autenticado
	else:
		return HttpResponseRedirect('/login')

#-------------------------------------------------------------------------------
#Si es alumno devuelve la lista de preguntas ya respondidas
#si es profesor devuelve lalista de preguntas almacenadas
#-------------------------------------------------------------------------------

def mispreguntas2(request):
	#csrftoken
	c={}
	c.update(csrf(request))
	if request.user.is_authenticated():
		template = get_template("registration/formulario2.html")
		usuario=request.user.username
		#si es staff
		if request.user.is_staff:
			if request.method=='GET':
				#miro el colegio del profesor para poder filtrar tb por colegio
				miusuario = User.objects.get(username=usuario)
				usuario_colegio = miusuario.persona.colegio
				#filtro por asignatura
				asignat=Asignaturas.objects.get(profesor=usuario, colegio=usuario_colegio)
				asignatura=asignat.asignatura
				
				listado=PreguntasCompletas.objects.all()
				listado=listado.extra(where=['asignatura=%s'], params=[asignatura])
				listado=listado.extra(where=['colegio=%s'], params=[usuario_colegio])
				
				
				return render_to_response('registration/formulario2.html', {'profesor':usuario, 'listadoprofesor':listado}, context_instance=RequestContext(request))
			#si no es GET muestro error
			else:
				return render_to_response('registration/formulario2.html', {'profesor':usuario,'error':"Error"}, context_instance=RequestContext(request))
		#si es alumno
		else:
			try:
				prespondidas=PreguntasRespondidas.objects.filter(usuario_no_pendiente=usuario)
				prespondidas=prespondidas.extra(order_by = ['-fecha'])

			except PreguntasRespondidas.DoesNotExist:
				prespondidas=''

			return render_to_response('registration/formulario2.html', {'alumno':usuario,'listadorespondidas':prespondidas }, context_instance=RequestContext(request))   
	else:
		return HttpResponseRedirect('/login')

#-------------------------------------------------------------------------------
#Para cambiar la contraseña
#-------------------------------------------------------------------------------

def conf(request):
	if request.user.is_authenticated():
		usuario=request.user.username
		if request.method=="GET":
			if request.user.is_staff:
				profesor=usuario
			else:
				profesor=''
			return render_to_response('registration/conf.html', {'user':usuario, 'profesor':profesor}, context_instance=RequestContext(request))

		if request.method == "POST":
			password1=request.POST['password']
			password2=request.POST['password2']

			if password1==password2:
				if not (len(password1)<6):
					u = User.objects.get(username__exact=usuario)
					u.set_password(password1)
					u.save()
					error=''
					exito="Contraseña modificada"
				else:
					error= "¡Error! La contraseña debe ser de al menos 6 caracteres"
					exito=''
			else:
				error= "¡Error! Las contraseñas deben coincidir"
				exito=''
			if request.user.is_staff:
				profesor=usuario
			else:
				profesor=''
			return render_to_response('registration/conf.html', {'user':'','profesor':profesor,'error':error, 'exito':exito}, context_instance=RequestContext(request))
			
	else:
		return HttpResponseRedirect('/login')



#-------------------------------------------------------------------------------
#Si es alumno devuelve las lecciones
#si es profesor formulario para añadir lecciones
#-------------------------------------------------------------------------------

def leccionnueva(request):
	#csrftoken
	c={}
	c.update(csrf(request))

	if request.user.is_authenticated():
		template = get_template("registration/leccionnueva.html")
		usuario=request.user.username
		#si es staff
		if request.user.is_staff:
			#si es profesor mostrará el formulario
			if request.method=='GET':
				return render_to_response('registration/leccionnueva.html', {'profesor':usuario}, context_instance=RequestContext(request))
			if request.method == "POST":
				leccion=request.POST['leccion']

				if (leccion==''):
					formFail= "¡Error! la lección está en blanco"
					return render_to_response('registration/leccionnueva.html', {'profesor':usuario,'error':formFail}, context_instance=RequestContext(request))
				else:
					#miramos si podemos notificar, y si va bien se lo comentamos al profesor
					try:

						#obtenemos todos los codigos de los usuarios
						#miro primero que asignatura imparte el profesor
						usuario=request.user.username
						
						#miro el colegio del profesor para poder filtrar tb por colegio
						miusuario = User.objects.get(username=usuario)
						usuario_colegio = miusuario.persona.colegio
						
						
						u=Asignaturas.objects.get(profesor=usuario, colegio=usuario_colegio)
						asignatura = u.asignatura
						#miro que alumno tiene matriculada la asignatura
						listadoalumnos= AsignaturasAlumno.objects.filter(asignatura=asignatura)

												
						#obtengo los codigos y posteriormente mirare si debo enviar o no
						listadocodigos= CodigosGCM.objects.all()
						
						statusGCM="ok"
						
						#quiero obtener solo los codigos GCM de los que esten matriculados
						for i in listadocodigos:
							for j in listadoalumnos:
								#si el alumno esta en esa asigntura le mando notificacion, sino no hago nada
								if (i.usuario==j.usuario):
							
									#convierto a smart_str para que no de erro de UnicodeEncodeError
									#asigna=smart_str(asignatura, encoding='utf-8')

									#convierto a smart_str para que no de erro de UnicodeEncodeError


									mens=asignatura+"=Nuevo aviso o consejo"
									mens = smart_str(mens)

									#para ello mando post a GCMServer 
									form_fields = {
										"registration_id": i.codigoGCM,#poner el del movil a enviar,
										"collapse_key": "test", #collapse_key is an arbitrary string (implement as you want)
										"data.msg": mens,
									}
									form_data = urllib.urlencode(form_fields)
									headers={'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8','Authorization': 'key=' + "AIzaSyCDoEsG-yNj8H-ObNJjeu39FxVtEk4fAWg"}
									#puerto por defecto para protocolo https 443
									conn = httplib.HTTPSConnection("android.googleapis.com", 443)
									conn.request("POST", "/gcm/send", form_data, headers)
		
									response = conn.getresponse()
									#mirar en http://docs.python.org/2/library/httplib.html codigos status y contemplar fallos
									data = response.read()

									conn.close()
									statusGCM="ok"
					except:
						statusGCM="fail"

					#si no se ha dado de alta el usuario en GCM no añadirle la pregunta
					if (statusGCM == "ok"):
						#miro la asignatura del profesor
						usuario=request.user.username
						
						#miro el colegio del profesor para poder filtrar tb por colegio
						miusuario = User.objects.get(username=usuario)
						usuario_colegio = miusuario.persona.colegio
						
						u=Asignaturas.objects.get(profesor=usuario,colegio=usuario_colegio)
						asignatura = u.asignatura
						
						fecha=datetime.now()
						record=Tips(leccion=leccion, fecha= fecha, asignatura=asignatura, colegio= usuario_colegio)
						record.save()

						form = "Tu lección se ha almacenado y notificado a los alumnos"
					if (statusGCM == "fail"):
						form = "No se han encontrado alumnos, lección no almacenada"

					return render_to_response('registration/leccionnueva.html', {'profesor':usuario,'exito':form}, context_instance=RequestContext(request))   
			#si no es ni GET ni POST
			else:
				return render_to_response('registration/leccionueva.html', {'profesor':usuario,'error':"Error"}, context_instance=RequestContext(request))
		#si es alumno
		else:
			return render_to_response('registration/leccionnueva.html', {'alumno':usuario,'error':"No tiene acceso"}, context_instance=RequestContext(request))   
	#si no esta autenticado
	else:
		return HttpResponseRedirect('/login')



#-------------------------------------------------------------------------------
#Lección por asignatura
#-------------------------------------------------------------------------------

def leccionporasignatura(request, asign):

	if request.user.is_authenticated():
		usuario=request.user.username
		if request.method=='GET':
			if request.user.is_staff:
				return HttpResponseRedirect('/home')
			else:
							
				#como la asignatura puede tener el mismo nombre en dos colegios distintos, le tengo que pasar el colegio
				#para ello, extraigo el colegio del usuario
				u = User.objects.get(username=usuario)
				usuario_colegio = u.persona.colegio
				try:
					listado=Tips.objects.all()
					listado=listado.extra(where=['colegio=%s'], params=[usuario_colegio])
					listado=listado.extra(where=['asignatura=%s'], params=[asign])
					listado=listado.extra(order_by = ['-fecha'])
					

				except Tips.DoesNotExist:
					listado=''

				return render_to_response('registration/leccion.html', {'alumno':usuario,'listadoalumno':listado }, context_instance=RequestContext(request))   
				

	else:
		return HttpResponseRedirect('/login')





#-------------------------------------------------------------------------------
#Tanto si es alumno como profesor devuelve la lista de lecciones
#-------------------------------------------------------------------------------

def leccion(request):
	#csrftoken
	c={}
	c.update(csrf(request))
	if request.user.is_authenticated():
		template = get_template("registration/formulario2.html")
		usuario=request.user.username
		#si es staff, por si añadimos nueva funcionalidad, por ahora es como si fuese un alumno
		if request.user.is_staff:
			if request.method=='GET':
				#obtengo el nombre de la asignatura con el nombre del profesor y su colegio					
				miusuario = User.objects.get(username=usuario)
				usuario_colegio = miusuario.persona.colegio
				
				asignat=Asignaturas.objects.get(profesor=usuario, colegio=usuario_colegio)
				asignatura=asignat.asignatura
				#filtro
				listado=Tips.objects.all()
				listado=listado.extra(where=['asignatura=%s'], params=[asignatura])
				listado=listado.extra(where=['colegio=%s'], params=[usuario_colegio])
				listado=listado.extra(order_by = ['-fecha'])
				return render_to_response('registration/leccion.html', {'profesor':usuario, 'listadoprofesor':listado}, context_instance=RequestContext(request))
			#si no es GET muestro error
			else:
				return render_to_response('registration/leccion.html', {'profesor':usuario,'error':"Error"}, context_instance=RequestContext(request))
		#si es alumno
		else:
			
			
			
			#le envio el listado de sus asignaturas matriculadas para que elija cual ranking quiere
			listaAsignaturas = AsignaturasAlumno.objects.filter(usuario=usuario)
			return render_to_response('registration/leccion.html', {'alumno':usuario,'listadoalumno':'', 'listaAsignaturas':listaAsignaturas }, context_instance=RequestContext(request))   		
			
			
			
			
			try:
				listado=Tips.objects.all()
				#obtengo el nombre de la asignatura con el nombre del profesor y su colegio					
				miusuario = User.objects.get(username=usuario)
				usuario_colegio = miusuario.persona.colegio
				listado=listado.extra(where=['colegio=%s'], params=[usuario_colegio])
				
				listado=listado.extra(order_by = ['-fecha'])
			except Tips.DoesNotExist:
				listado=''
			return render_to_response('registration/leccion.html', {'alumno':usuario,'listadoalumno':listado }, context_instance=RequestContext(request))   
	else:
		return HttpResponseRedirect('/login')





#-------------------------------------------------------------------------------
#prueba GCM
#
#-------------------------------------------------------------------------------

def pruebagcm(request):

	if request.user.is_authenticated():
		usuario=request.user.username
		if request.method=="GET":
			if request.user.is_staff:
				profesor=usuario
			else:
				profesor=''
			return render_to_response('registration/pruebagcm.html', {'user':usuario, 'profesor':profesor}, context_instance=RequestContext(request))

		if request.method == "POST":
			usuario=request.POST['user']

			try:
				u=CodigosGCM.objects.get(usuario=usuario)
				codigogcm = u.codigoGCM
				#si existe el usuario, le hago llegar la notificacion a el otro usuario

				#para ello mando post a GCMServer 
				form_fields = {
					"registration_id": codigogcm,#poner el del movil a enviar,
					"collapse_key": "test", #collapse_key is an arbitrary string (implement as you want)
					"data.msg": "testeando",
				}
				form_data = urllib.urlencode(form_fields)
				headers={'Content-Type': 'application/x-www-form-urlencoded','Authorization': 'key=' + "AIzaSyCDoEsG-yNj8H-ObNJjeu39FxVtEk4fAWg"}
				#puerto por defecto para protocolo https 443
				conn = httplib.HTTPSConnection("android.googleapis.com", 443)
				conn.request("POST", "/gcm/send", form_data, headers)

				response = conn.getresponse()
				print response.status
				#mirar en http://docs.python.org/2/library/httplib.html codigos status y contemplar fallos
				data = response.read()
				print data
				conn.close()

				error=''
				exito="enviado"


			except:
				error= "Usuario no encontrado"
				exito=''			


			if request.user.is_staff:
				profesor=usuario
			else:
				profesor=''
			return render_to_response('registration/pruebagcm.html', {'user':'','profesor':profesor,'error':error, 'exito':exito}, context_instance=RequestContext(request))
			
	else:
		return HttpResponseRedirect('/login')


#-------------------------------------------------------------------------------
#gráfica que devuelve las puntuaciones de tus alumnos
#solo profesor
#-------------------------------------------------------------------------------


def graficapuntosasign(request):
	
	if request.user.is_authenticated():
		usuario=request.user.username
		if request.method=="GET":
			if request.user.is_staff:
				#miro el colegio del alumno para poder filtrar tb por colegio
				miusuario = User.objects.get(username=usuario)
				usuario_colegio = miusuario.persona.colegio
				#obtengo su asignatura
				asignat=Asignaturas.objects.get(profesor=usuario, colegio=usuario_colegio)
				asignatura=asignat.asignatura

				
				
				punt=Puntuaciones.objects.all()
				#filtro por asignatura
				punt = punt.extra(where=['asignatura=%s'], params=[asignatura])
				punt = punt.extra(where=['colegio=%s'], params=[usuario_colegio])
				punt=punt.extra(order_by = ['-puntos'])


				return render_to_response('charts/puntuaciones.html', {'asignatura':asignatura, 'puntuaciones':punt}, context_instance=RequestContext(request))

				
			else:
				return HttpResponseRedirect('/home')

		else:#si no es GET
			return HttpResponseRedirect('/home')

			
	else:
		return HttpResponseRedirect('/login')
	
	
	
#-------------------------------------------------------------------------------
#devuelvo usuarios para que pueda elegir uno
#solo profesor
#-------------------------------------------------------------------------------


def graficatiempo(request):
	
	if request.user.is_authenticated():
		usuario=request.user.username
		if request.method=="GET":
			if request.user.is_staff:
				#miro el colegio del alumno para poder filtrar tb por colegio
				miusuario = User.objects.get(username=usuario)
				usuario_colegio = miusuario.persona.colegio
				#obtengo su asignatura
				asignat=Asignaturas.objects.get(profesor=usuario, colegio=usuario_colegio)
				asignatura=asignat.asignatura

				
				listadoalumnos= AsignaturasAlumno.objects.filter(asignatura=asignatura)
				
				
				
				return render_to_response('registration/grafica.html', {'listadoalumnos':listadoalumnos}, context_instance=RequestContext(request))

				
			else:
				return HttpResponseRedirect('/home')

		else:#si no es GET
			return HttpResponseRedirect('/home')

			
	else:
		return HttpResponseRedirect('/login')
	
	
#-------------------------------------------------------------------------------
#devuelvo gráfica por usuario del tiempo ocioso
#solo profesor
#-------------------------------------------------------------------------------
def graficatiempousuario(request, user):
	
	if request.user.is_authenticated():
		usuario=request.user.username
		if request.method=="GET":
			if request.user.is_staff:
				tocio=MedidaOcioDiaria.objects.filter(usuario=user)
				#filtro por asignatura
				#tocio = tocio.extra(where=['usuario=%s'], params=[usuario])
				tocio=tocio.extra(order_by = ['-fecha'])



				return render_to_response('charts/tiempoociosoalumno.html', {'tocio':tocio}, context_instance=RequestContext(request))

				
			else:
				return HttpResponseRedirect('/home')

		else:#si no es GET
			return HttpResponseRedirect('/home')

			
	else:
		return HttpResponseRedirect('/login')


#-------------------------------------------------------------------------------
#devuelve la gráfica con los tipos de preguntas hechas por los usuarios
#para profesor y alumno, en caso de alumno lo hace por asignatura
#-------------------------------------------------------------------------------

def graficatipopreguntas(request, asign):
	
	if request.user.is_authenticated():
		usuario=request.user.username
		if request.method=="GET":
			if request.user.is_staff:
				#miro el colegio del alumno para poder filtrar tb por colegio
				miusuario = User.objects.get(username=usuario)
				usuario_colegio = miusuario.persona.colegio
				#obtengo su asignatura
				asignat=Asignaturas.objects.get(profesor=usuario, colegio=usuario_colegio)
				asignatura=asignat.asignatura

				punt=Puntuaciones.objects.all()
				#filtro por asignatura
				punt = punt.extra(where=['asignatura=%s'], params=[asignatura])
				punt = punt.extra(where=['colegio=%s'], params=[usuario_colegio])

				return render_to_response('charts/tipopreguntas.html', {'asignatura':asignatura, 'puntuaciones':punt}, context_instance=RequestContext(request))

				
			else:
			#si es alumno
				try:
					punt=Puntuaciones.objects.filter(usuario=usuario)
					punt = punt.extra(where=['asignatura=%s'], params=[asign])
				except:
					error= "No se han encontrado datos"
					return render_to_response('registration/grafica.html', {'error':error}, context_instance=RequestContext(request))

				return render_to_response('charts/tipopreguntasalumno.html', {'puntuaciones':punt, 'asignatura':asign}, context_instance=RequestContext(request))


		else:#si no es GET
			return HttpResponseRedirect('/home')

			
	else:
		return HttpResponseRedirect('/login')
	
#-------------------------------------------------------------------------------
#devuelve la gráfica con las respuestas correctas e incorrectas por alumno
#para profesor y alumno
#-------------------------------------------------------------------------------

def graficaaciertos(request, asign):
	
	if request.user.is_authenticated():
		usuario=request.user.username
		if request.method=="GET":
			if request.user.is_staff:
				#miro el colegio del alumno para poder filtrar tb por colegio
				miusuario = User.objects.get(username=usuario)
				usuario_colegio = miusuario.persona.colegio
				#obtengo su asignatura
				asignat=Asignaturas.objects.get(profesor=usuario, colegio=usuario_colegio)
				asignatura=asignat.asignatura

				punt=Puntuaciones.objects.all()
				#filtro por asignatura
				punt = punt.extra(where=['asignatura=%s'], params=[asignatura])
				punt = punt.extra(where=['colegio=%s'], params=[usuario_colegio])


				return render_to_response('charts/aciertosfallos.html', {'asignatura':asignatura, 'puntuaciones':punt}, context_instance=RequestContext(request))

				
			else:
			#si es alumno
				try:
					punt=Puntuaciones.objects.filter(usuario=usuario)
					punt = punt.extra(where=['asignatura=%s'], params=[asign])
					
				except:
					error= "No se han encontrado datos"
					return render_to_response('registration/grafica.html', {'error':error}, context_instance=RequestContext(request))


				return render_to_response('charts/aciertosfallosalumno.html', {'puntuaciones':punt, 'asignatura':asign}, context_instance=RequestContext(request))


		else:#si no es GET
			return HttpResponseRedirect('/home')

			
	else:
		return HttpResponseRedirect('/login')




#-------------------------------------------------------------------------------
#mostraremos el listado de asignaturas para mostrar las graficas
#-------------------------------------------------------------------------------

def grafica(request):

	template = get_template("registration/grafica.html")
	if request.user.is_authenticated():
		usuario=request.user.username
		if request.method=='GET':
			if request.user.is_staff:
				return render_to_response('registration/grafica.html', {'lista':"true", 'profesor':usuario}, context_instance=RequestContext(request))
			#si es alumno
			else:
				#le envio el listado de sus asignaturas matriculadas para que elija cual asignatura quiere
				listaAsignaturas = AsignaturasAlumno.objects.filter(usuario=usuario)

				return render_to_response('registration/grafica.html', {'alumno':usuario, 'listaAsignaturas':listaAsignaturas}, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/login')
	
#-------------------------------------------------------------------------------
#mostraremos el listado de posibles graficas
#-------------------------------------------------------------------------------
def graficaporasignatura(request, asign):

	template = get_template("registration/grafica.html")
	if request.user.is_authenticated():
		usuario=request.user.username
		if request.method=='GET':
			if request.user.is_staff:
				return render_to_response('registration/grafica.html', {'lista':"true",'profesor':usuario}, context_instance=RequestContext(request))
			#si es alumno
			else:
				return render_to_response('registration/grafica.html', {'lista':"true",'alumno':usuario, 'asignatura':asign}, context_instance=RequestContext(request))
	else:
		return HttpResponseRedirect('/login')




################################################################################
#------------------------------------------------------------------------------#
#							ANDROID											   #
#------------------------------------------------------------------------------#
################################################################################

#-------------------------------------------------------------------------------
#Login
#-------------------------------------------------------------------------------

def androidlogin(request):

	#csrftoken
	c={}
	c.update(csrf(request))

	if request.method == "POST":

		username = request.POST['user']
		password = request.POST['password']
		type = request.POST['type']
		idmovil = request.POST['idmovil']



		user = authenticate(username=username, password=password)

		if user is None:
			return HttpResponseServerError()

		else:
			print unicode(csrf(request)['csrf_token'])
			return HttpResponse('',unicode(c))

		print unicode(csrf(request)['csrf_token'])
		return HttpResponse('',unicode(c))

	elif request.method == "GET":

		print unicode(csrf(request)['csrf_token'])
		return HttpResponse('',unicode(c))

#-------------------------------------------------------------------------------
#Recibimos la respuesta dada por el alumno y anotamos
#-------------------------------------------------------------------------------


def androidenviarespuestas(request):
	#csrftoken
	c={}
	c.update(csrf(request))
	
	if request.method == "POST":

		respuesta_usuario = request.POST['respuesta']
		pregunta = request.POST['pregunta']
		usuario = request.POST['usuario']
		asignatura = request.POST['asignatura']

		#filtramos también por asignatura ya que puede haber dos preg iguales en distinto cursos
		question3=PreguntasVisibles.objects.get(usuario_pendiente=usuario,pregunta=pregunta, asignatura=asignatura)
		#miramos de que tipo es la pregunta para contabilizar puntos
		tipoPregunta=question3.tag
		question3.delete()

		#comprobamos si es correcta
		question2=PreguntasCompletas.objects.get(pregunta=pregunta,asignatura= asignatura)

		if respuesta_usuario == question2.respuesta:
			escorrecta=question2.respuesta1_correcta
		elif respuesta_usuario == question2.respuesta2:
			escorrecta=question2.respuesta2_correcta
		elif respuesta_usuario == question2.respuesta3:
			escorrecta=question2.respuesta3_correcta

		#anotamos lo puntos ganados con esta pregunta en la correspondiente asignatura	
		usuario_puntos=Puntuaciones.objects.get(usuario=usuario, asignatura=asignatura)

		
		if escorrecta == "true":
			usuario_puntos.npreguntascorrectas=usuario_puntos.npreguntascorrectas+1
			if tipoPregunta=="obligada":
				usuario_puntos.puntos=usuario_puntos.puntos+2
			elif tipoPregunta=="extra":
				usuario_puntos.puntos=usuario_puntos.puntos+3
			else:
				usuario_puntos.puntos=usuario_puntos.puntos+1
		else:
			usuario_puntos.npreguntasincorrectas=usuario_puntos.npreguntasincorrectas+1
			if tipoPregunta=="obligada":
				usuario_puntos.puntos=usuario_puntos.puntos-1
			elif tipoPregunta=="extra":
				usuario_puntos.puntos=usuario_puntos.puntos-1
			else:
				usuario_puntos.puntos=usuario_puntos.puntos-2
			
		usuario_puntos.save()

		#miramos cual era la correcta
		if question2.respuesta1_correcta == "true":
			verdadera=question2.respuesta
		elif question2.respuesta2_correcta == "true":
			verdadera=question2.respuesta2
		elif question2.respuesta3_correcta == "true":
			verdadera=question2.respuesta3

		fecha=datetime.now()

		record=PreguntasRespondidas(usuario_no_pendiente=usuario,pregunta=pregunta,respuesta=verdadera, respuesta_dada=respuesta_usuario, respuesta_usuario_correcta=escorrecta, fecha=fecha, asignatura=asignatura)
		record.save()


		print unicode(csrf(request)['csrf_token'])
		return HttpResponse(escorrecta,unicode(c))
	elif request.method == "GET":
		print unicode(csrf(request)['csrf_token'])
		return HttpResponse('',unicode(c))

#-------------------------------------------------------------------------------
#devuelve las preguntas pendientes para el alumno
#-------------------------------------------------------------------------------

def androidpidepreguntas(request, usuario):
	
	#csrftoken
	c={}
	c.update(csrf(request))

	#user= usuario
	#así selcciono de la base de datos, solo las preguntas dirigidas a los usuarios y los campos que solo necesito para no desvelar las respuestas
	#data = serializers.serialize("json", PreguntasVisibles.objects.filter(usuario_pendiente=user), fields=('usuario_pendiente','pregunta', 'respuesta', 'respuesta2', 'respuesta3', 'tag'))
	#return HttpResponse("{\"preguntas\":"+data+"}")
	
	if request.method == "POST":
		user= usuario
		asignatura = request.POST['asignatura']
		p=PreguntasVisibles.objects.filter(usuario_pendiente=user)
		#filtro por asignatura
		p=p.extra(where=['asignatura=%s'], params=[asignatura])
		data = serializers.serialize("json", p, fields=('usuario_pendiente','pregunta', 'respuesta', 'respuesta2', 'respuesta3', 'tag'))
		return HttpResponse("{\"preguntas\":"+data+"}")


	elif request.method == "GET":

		print unicode(csrf(request)['csrf_token'])
		return HttpResponse('',unicode(c))

	

#-------------------------------------------------------------------------------
#Devuelve el listado de las preguntas realizadas
#-------------------------------------------------------------------------------

def androidlistacorrectas(request, usuario):
	#csrftoken
	c={}
	c.update(csrf(request))

	#user= usuario
	#p=PreguntasRespondidas.objects.filter(usuario_no_pendiente=user)
	#p=p.extra(order_by = ['-fecha'])
	#así selcciono de la base de datos, solo las preguntas dirigidas a los usuarios y los campos que solo necesito para no desvelar las respuestas
	#data = serializers.serialize("json", p, fields=('pregunta', 'respuesta', 'respuesta_dada', 'respuesta_usuario_correcta'))
	#return HttpResponse("{\"preguntas\":"+data+"}")
	
	if request.method == "POST":
		user= usuario
		asignatura = request.POST['asignatura']
		p=PreguntasRespondidas.objects.filter(usuario_no_pendiente=user)
		#filtro por asignatura
		p=p.extra(where=['asignatura=%s'], params=[asignatura])
		p=p.extra(order_by = ['-fecha'])
		data = serializers.serialize("json", p, fields=('pregunta', 'respuesta', 'respuesta_dada', 'respuesta_usuario_correcta'))
		return HttpResponse("{\"preguntas\":"+data+"}")


	elif request.method == "GET":

		print unicode(csrf(request)['csrf_token'])
		return HttpResponse('',unicode(c))
	

#-------------------------------------------------------------------------------
#devuelve el ranking de alumnos por puntos
#-------------------------------------------------------------------------------

def androidclasificacion(request, usuario):

	#p=Puntuaciones.objects.all()
	#p=p.extra(order_by = ['-puntos'])
	#data = serializers.serialize("json",p, fields=('usuario','puntos'))
	#return HttpResponse("{\"puntos\":"+data+"}")
	
	#csrftoken
	c={}

	c.update(csrf(request))

	
	if request.method == "POST":

		asignatura = request.POST['asignatura']
		
		
		#miro el colegio del alumno para poder filtrar tb por colegio
		miusuario = User.objects.get(username=usuario)
		usuario_colegio = miusuario.persona.colegio
		
		
		punt=Puntuaciones.objects.all()
		#filtro por asignatura
		punt = punt.extra(where=['asignatura=%s'], params=[asignatura])
		punt = punt.extra(where=['colegio=%s'], params=[usuario_colegio])
		punt=punt.extra(order_by = ['-puntos'])

		data = serializers.serialize("json",punt, fields=('usuario','puntos'))
		return HttpResponse("{\"puntos\":"+data+"}")


	elif request.method == "GET":

		c=unicode(csrf(request)['csrf_token'])
		return HttpResponse('',c)


#-------------------------------------------------------------------------------
#añade una nueva pregunta debido al ocio para responder al usuario
#-------------------------------------------------------------------------------

def androidsumapregunta(request, usuario):

	user= usuario
	try:
		p = PreguntasPendientes.objects.filter(usuario_pendiente=user)
		print "lego aqui1"
		usuario_pendiente = p[0].usuario_pendiente
		print "lego aqui2"
		pregunta = p[0].pregunta
		respuesta= p[0].respuesta
		respuesta2= p[0].respuesta2
		respuesta3= p[0].respuesta3
		asignatura= p[0].asignatura
		p[0].delete()
		print "si hay pregunta"

		record=PreguntasVisibles(usuario_pendiente=usuario_pendiente,pregunta=pregunta,respuesta=respuesta,respuesta2=respuesta2, respuesta3=respuesta3, tag="obligada", asignatura=asignatura)
		record.save()
		print "la guardo"

		#le incrementamos el contador de preguntas obligadas
		pobligada=Puntuaciones.objects.get(usuario=user, asignatura=asignatura)
		pobligada.preguntaobligada=pobligada.preguntaobligada+1
		pobligada.save()

	
		

		#convierto a smart_str para que no de erro de UnicodeEncodeError
		mensa="ok="+asignatura
		mensa = smart_str(mensa)

		return HttpResponse(mensa)
	except:
		return HttpResponse("fail=fail")
	
	
	
	
	
	
#-------------------------------------------------------------------------------
#incremento de tiempo ocioso
#-------------------------------------------------------------------------------

def androidsumatiempoocioso(request, usuario):	
	
	#incrementamos su contador de "tiempo" ocioso
	hoy=date.today()
	print hoy
	try:
		#intento obtener de la base de datos(coincida dia y usuario), si no existe lo creo
		#incremento 30 min ya que es lo que tiene puesto la app para lanzar notificaciones
		tOcioso=MedidaOcioDiaria.objects.get(usuario=usuario, fecha=hoy)
		tOcioso.nPreguntasdia=tOcioso.nPreguntasdia+30
	#si no se encuentra lo creo, y le inicializo nPReguntasdiaa 1
	except:
		record1=MedidaOcioDiaria(usuario=usuario,fecha=hoy,nPreguntasdia=30)
		record1.save()
	#recordar que es una medida estimada
	return HttpResponse("ok")

#-------------------------------------------------------------------------------
#devuelve el listado de lecciones para los alumnos
#-------------------------------------------------------------------------------

def androidtips(request):
	
	#csrftoken
	c={}
	c.update(csrf(request))

	#l=Tips.objects.all()
	#l=l.extra(order_by = ['-fecha'])
	#data = serializers.serialize("json",l, fields=('leccion'))
	#return HttpResponse("{\"tips\":"+data+"}")
	
	if request.method == "POST":
		
		asignatura = request.POST['asignatura']
		usuario= request.POST['usuario']
		
		#miro el colegio del alumno para poder filtrar tb por colegio
		miusuario = User.objects.get(username=usuario)
		usuario_colegio = miusuario.persona.colegio
		
		
		l=Tips.objects.all()
		#filtro por asignatura
		l = l.extra(where=['asignatura=%s'], params=[asignatura])
		#filtro por colegio
		l = l.extra(where=['colegio=%s'], params=[usuario_colegio])
		l=l.extra(order_by = ['-fecha'])
		data = serializers.serialize("json",l, fields=('leccion'))	
		return HttpResponse("{\"tips\":"+data+"}")


	elif request.method == "GET":

		print unicode(csrf(request)['csrf_token'])
		return HttpResponse('',unicode(c))
	

#-------------------------------------------------------------------------------
#añade una pregunta extra para responder al usuario y le suma 1 a preguntaextra
#-------------------------------------------------------------------------------

def androidpreguntaextra(request, usuario):

	#csrftoken
	c={}
	c.update(csrf(request))


	if request.method == "POST":
		asignatura = request.POST['asignatura']
		user= usuario
		try:
			p = PreguntasPendientes.objects.filter(usuario_pendiente=user)
			p = p.extra(where=['asignatura=%s'], params=[asignatura])
		
			usuario_pendiente = p[0].usuario_pendiente
			pregunta = p[0].pregunta
			respuesta= p[0].respuesta
			respuesta2= p[0].respuesta2
			respuesta3= p[0].respuesta3
			asignatura= p[0].asignatura
			p[0].delete()
	
	
			record=PreguntasVisibles(usuario_pendiente=usuario_pendiente,pregunta=pregunta,respuesta=respuesta,respuesta2=respuesta2, respuesta3=respuesta3, tag="extra", asignatura= asignatura)
			record.save()
	
			#le incrementamos el contador de preguntas extras
			pextra=Puntuaciones.objects.get(usuario=user, asignatura=asignatura)
			pextra.preguntaextra=pextra.preguntaextra+1
			pextra.save()
	
			return HttpResponse("ok")
		except:
			return HttpResponse("fail")
	
	elif request.method == "GET":
		print unicode(csrf(request)['csrf_token'])
		return HttpResponse('',unicode(c))


#-------------------------------------------------------------------------------
#Registro codigoGCM usuario
#-------------------------------------------------------------------------------
def androidgcmregistrocliente(request):
	print request
	#csrftoken
	c={}
	c.update(csrf(request))

	if request.method == "POST":

		usuario = request.POST['user']
		codigoGCM = request.POST['codigoGCM']

		try:
			#miramos si ya tenia codigo y si lo tiene lo actualizamos
			c=CodigosGCM.objects.get(usuario=usuario)
			c.codigoGCM=codigoGCM
			c.save()
		except:
			#si no lo teníamos lo guardamos
			record=CodigosGCM(usuario=usuario,codigoGCM=codigoGCM)
			record.save()

		print unicode(csrf(request)['csrf_token'])
		return HttpResponse('',unicode(c))

	elif request.method == "GET":
		print unicode(csrf(request)['csrf_token'])
		return HttpResponse('',unicode(c))

#-------------------------------------------------------------------------------
#Envío de preguntas a otros compañeros
#-------------------------------------------------------------------------------

def androidenviapreguntaextra(request, emisor, receptor):

	#csrftoken
	c={}
	c.update(csrf(request))
	statusGCM=""

	if request.method == "POST":
		asignatura = request.POST['asignatura']
		
		try:
			#miramos también si exiten preguntas disponibles y de la asignatura marcada
			pre = PreguntasPendientes.objects.filter(usuario_pendiente=receptor)
			pre = pre.extra(where=['asignatura=%s'], params=[asignatura])
			probamos= pre[0].pregunta
			statusGCM="ok"
			try:
				#miramos también si exite eñ usuario
	
				u=CodigosGCM.objects.get(usuario=receptor)
				codigogcm = u.codigoGCM
				statusGCM="ok"
	
				#si existe el receptor, le hago llegar la notificacion
			except:
				statusGCM="fail"
		except:
			statusGCM="failNoPregunta"



		if (statusGCM=="ok"):
			#para ello mando post a GCMServer 
			
			#convierto a smart_str para que no de erro de UnicodeEncodeError
			mensa=asignatura+"=Te ha enviado una pregunta "+emisor
			mensa = smart_str(mensa)
			
			
			
			
			form_fields = {
				"registration_id": codigogcm,#poner el del movil a enviar,
				"collapse_key": "test", #collapse_key is an arbitrary string (implement as you want)
				"data.msg": mensa,
			}
			form_data = urllib.urlencode(form_fields)
			headers={'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8','Authorization': 'key=' + "AIzaSyCDoEsG-yNj8H-ObNJjeu39FxVtEk4fAWg"}
			#puerto por defecto para protocolo https 443
			conn = httplib.HTTPSConnection("android.googleapis.com", 443)
			conn.request("POST", "/gcm/send", form_data, headers)
			try:
				response = conn.getresponse()
				print response.status
				#mirar en http://docs.python.org/2/library/httplib.html codigos status y contemplar fallos
				data = response.read()

				conn.close()
				statusGCM="ok"
			except:
				statusGCM="noRed"
	
	
	
		#si no se ha dado de alta el usuario en GCM no añadirle la pregunta
		if (statusGCM == "ok"):
			try:
				#intentamos añadir la pregunta al receptor
				p = PreguntasPendientes.objects.filter(usuario_pendiente=receptor)
				p = p.extra(where=['asignatura=%s'], params=[asignatura])	
					
				usuario_pendiente = p[0].usuario_pendiente
				pregunta = p[0].pregunta
				respuesta= p[0].respuesta
				respuesta2= p[0].respuesta2
				respuesta3= p[0].respuesta3
				asignatura= p[0].asignatura
				p[0].delete()
	
	
				record=PreguntasVisibles(usuario_pendiente=usuario_pendiente,pregunta=pregunta,respuesta=respuesta,respuesta2=respuesta2, respuesta3=respuesta3, tag="amistosa enviada por "+emisor, asignatura=asignatura)
				record.save()
	
				#le incrementamos el contador de preguntas amistosas recibidas y 
				# enviadas (emisor y receptor)
				pamistosa=Puntuaciones.objects.get(usuario=receptor, asignatura=asignatura)
				pamistosa.preguntarecibidaamistosa=pamistosa.preguntarecibidaamistosa+1
				pamistosa.save()
	
				pamistosa2=Puntuaciones.objects.get(usuario=emisor, asignatura=asignatura)
				pamistosa2.preguntaenviadaamistosa=pamistosa2.preguntaenviadaamistosa+1
				pamistosa2.save()
	
				return HttpResponse("ok")
			except:
				return HttpResponse("fail")
	
		elif (statusGCM == "fail"):
			return HttpResponse("no_user")
		
		elif (statusGCM == "failNoPregunta"):
			return HttpResponse("fail")
	
		elif (statusGCM == "noRed"):
			return HttpResponse("no_red")
		
	elif request.method == "GET":

		print unicode(csrf(request)['csrf_token'])
		return HttpResponse('',unicode(c))
		
#-------------------------------------------------------------------------------
#devuelve el listado completo de asignaturas
#-------------------------------------------------------------------------------

def androidasignaturascompleto(request, usuario):

	#miro el colegio del alumno para poder filtrar tb por colegio
	miusuario = User.objects.get(username=usuario)
	usuario_colegio = miusuario.persona.colegio


	l=Asignaturas.objects.all()
	l = l.extra(where=['colegio=%s'], params=[usuario_colegio])
	
	#l=l.extra(order_by = ['-profesor'])
	data = serializers.serialize("json",l, fields=('asignatura','profesor'))
	return HttpResponse("{\"asignaturas\":"+data+"}")

#-------------------------------------------------------------------------------
#devuelve el listado de las asignaturas matriculadas
#-------------------------------------------------------------------------------

def androidasignaturasusuario(request, usuario):

	l=AsignaturasAlumno.objects.filter(usuario=usuario)
	data = serializers.serialize("json",l, fields=('asignatura'))
	return HttpResponse("{\"asignaturasalumno\":"+data+"}")

#-------------------------------------------------------------------------------
#matricula a un usuario de una asignatura
#-------------------------------------------------------------------------------

def androidasignaturasmatricula(request):
	
	#csrftoken
	c={}
	c.update(csrf(request))
	
	if request.method == "POST":
		
		usuario = request.POST['usuario']
		asignatura = request.POST['asignatura']
		
		#miro el colegio del alumno para poder filtrar tb por colegio
		miusuario = User.objects.get(username=usuario)
		usuario_colegio = miusuario.persona.colegio
		

		try:
			#miramos si ya existe la matricula
			matrics = AsignaturasAlumno.objects.filter(usuario=usuario)
			matrics = matrics.extra(where=['asignatura=%s'], params=[asignatura])
			
			if (matrics[0].asignatura == ''):
				statusMatricula="ok"
	
			else:
				statusMatricula="exist"
				
			
		except:
			statusMatricula="ok"
			
		if (statusMatricula=="ok"):
			#cuando se matricule de la asignatura le añadimos la puntuación y las preguntas que haya hasta el momento
			#añadimos a la tabla de puntuaciones
			puntuaciones= Puntuaciones(usuario=usuario, puntos=0, preguntaextra=0, preguntaobligada=0, preguntarecibidaamistosa=0, preguntaenviadaamistosa=0, asignatura=asignatura, colegio=usuario_colegio, npreguntascorrectas=0,npreguntasincorrectas=0);
			puntuaciones.save()
			
			#añadimos las preguntas existentes al nuevo usuario para que disponga de todas (no olvidar filtrar por asignatura y colegio)
			listadopreguntas= PreguntasCompletas.objects.filter(asignatura=asignatura, colegio=usuario_colegio)
			for i in listadopreguntas:
				usuario_pendiente = usuario
				pregunta= i.pregunta
				respuesta= i.respuesta
				respuesta2= i.respuesta2
				respuesta3= i.respuesta3
				record=PreguntasPendientes(usuario_pendiente=usuario_pendiente,pregunta=pregunta,respuesta=respuesta,respuesta2=respuesta2, respuesta3=respuesta3, asignatura=asignatura)
				record.save()			
			
			
			#almaceno la asignatura en la que se acaba de matricular
			record=AsignaturasAlumno(usuario=usuario,asignatura=asignatura)
			record.save()
			print "ok"
			return HttpResponse("ok")
		else:
			print "exist"
			return HttpResponse("exist")
		
	elif request.method == "GET":

		print unicode(csrf(request)['csrf_token'])
		return HttpResponse('',unicode(c))
	
	
	
	
	




			