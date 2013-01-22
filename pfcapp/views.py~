# -*- encoding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound, HttpRequest, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from pfcapp.models import PreguntasPendientes, PreguntasCompletas, PreguntasRespondidas, Puntuaciones, PreguntasVisibles, Tips
from django.core.context_processors import csrf
from django.contrib.auth import authenticate

from django.template.loader import get_template
from django.template import Context, RequestContext

from django.utils import simplejson
from django.core import serializers

from datetime import datetime

#-------------------------------------------------------------------------------
#mostraremos el ranking
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
			else:
				profesor=''
			return HttpResponse(template.render(Context({'user':usuario,'profesor':profesor,'ranking':ranking})))
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
			username=request.POST['user']
			if username=="":
				signFail= "Error! Debes rellenar todos los campos"
				return render_to_response('registration/signin.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
			else:
				try:
					u = User.objects.get(username__exact=username)
					if str(u) == str(username):
						signFail= "Error! El usuario "+username +" ya existe, pruebe de nuevo con otro usuario"
						return render_to_response('registration/signin.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
				except User.DoesNotExist:
					password=request.POST['password']
					password2=request.POST['password2']

					email=request.POST['email']
					if (password=="") or (email==""):
						signFail= "Error! Debes rellenar todos los campos"
						return render_to_response('registration/signin.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
					elif (len(password)<6):
						signFail= "Error! La contraseña debe ser de al menos 6 caracteres"
						return render_to_response('registration/signin.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
					elif (password2!=password):
						signFail= "Error! Los campos de la contraseña deben coincidir"
						return render_to_response('registration/signin.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
					else:
						user = User.objects.create_user(username,email,password)
						user.save()
						#añadimos a la tabla de puntuaciones
						puntuaciones= Puntuaciones(usuario=username, puntos=0, preguntaextra=0, preguntaobligada=0);
						puntuaciones.save()

						#añadimos las preguntas existentes al nuevo usuario para que disponga de todas
						listadopreguntas= PreguntasCompletas.objects.all()
						for i in listadopreguntas:
							usuario_pendiente = username
							pregunta= i.pregunta
							respuesta= i.respuesta
							respuesta2= i.respuesta2
							respuesta3= i.respuesta3
							record=PreguntasPendientes(usuario_pendiente=usuario_pendiente,pregunta=pregunta,respuesta=respuesta,respuesta2=respuesta2, respuesta3=respuesta3)
							record.save()

						sign = "Tu registro se ha realizado con éxito"
						return render_to_response('registration/signin.html', {'user':username,'exito':sign}, context_instance=RequestContext(request))
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
			return render_to_response('registration/signinprofesor.html',c)
		if request.method == "POST":
			CLAVE_ADMIN="efsmcegqempsecelmcemqeg"
			clave=request.POST['clave']
			if CLAVE_ADMIN == clave:

				username=request.POST['user']
				if username=="":
					signFail= "Error! Debes rellenar todos los campos"
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

						email=request.POST['email']
						if (password=="") or (email==""):
							signFail= "Error! Debes rellenar todos los campos"
							return render_to_response('registration/signinprofesor.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
						elif (len(password)<6):
							signFail= "Error! La contraseña debe ser de al menos 6 caracteres"
							return render_to_response('registration/signinprofesor.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
						elif (password2!=password):
							signFail= "Error! Los campos de la contraseña deben coincidir"
							return render_to_response('registration/signinprofesor.html', {'user':'','error':signFail}, context_instance=RequestContext(request))
						else:
							user = User.objects.create_user(username,email,password)
							# staff solo para el profesor
							user.is_staff = True
							user.save()

							sign = "Tu registro se ha realizado con éxito"
							return render_to_response('registration/signinprofesor.html', {'user':username,'exito':sign}, context_instance=RequestContext(request))
			#si la clave admin no coincide
			else:
				signFail= "Error! Introduce correctamente la clave dada por el administrador"
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
			
					record=PreguntasCompletas(pregunta=pregunta,respuesta=respuesta,respuesta1_correcta=respuesta1_correcta ,respuesta2=respuesta2,respuesta2_correcta=respuesta2_correcta, respuesta3=respuesta3,respuesta3_correcta=respuesta3_correcta)
					record.save()

					for i in Usuarios:
						usuario_pendiente = i.username
				
						record2=PreguntasPendientes(usuario_pendiente=usuario_pendiente,pregunta=pregunta,respuesta=respuesta,respuesta2=respuesta2, respuesta3=respuesta3)
						record2.save()

					form = "Tu pregunta se ha almacenado."
					return render_to_response('registration/formulario1.html', {'profesor':usuario,'exito':form}, context_instance=RequestContext(request))   
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
				listado=PreguntasCompletas.objects.all()
				return render_to_response('registration/formulario2.html', {'profesor':usuario, 'listadoprofesor':listado}, context_instance=RequestContext(request))
			#si no es GET muestro error
			else:
				return render_to_response('registration/formulario2.html', {'profesor':usuario,'error':"Error"}, context_instance=RequestContext(request))
		#si es alumno
		else:
			try:
				prespondidas=PreguntasRespondidas.objects.filter(usuario_no_pendiente=usuario)
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
					error= "Error! La contraseña debe ser de al menos 6 caracteres"
					exito=''
			else:
				error= "Error! Las contraseñas deben coincidir"
				exito=''
			if request.user.is_staff:
				profesor=usuario
			else:
				profesor=''
			return render_to_response('registration/conf.html', {'user':'','profesor':profesor,'error':error, 'exito':exito}, context_instance=RequestContext(request))
			
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
				listado=Tips.objects.all()
				listado=listado.extra(order_by = ['-fecha'])
				return render_to_response('registration/leccion.html', {'profesor':usuario, 'listadoprofesor':listado}, context_instance=RequestContext(request))
			#si no es GET muestro error
			else:
				return render_to_response('registration/leccion.html', {'profesor':usuario,'error':"Error"}, context_instance=RequestContext(request))
		#si es alumno
		else:
			try:
				listado=Tips.objects.all()
				listado=listado.extra(order_by = ['-fecha'])
			except PreguntasRespondidas.DoesNotExist:
				listado=''
			return render_to_response('registration/leccion.html', {'alumno':usuario,'listadoalumno':listado }, context_instance=RequestContext(request))   
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
					formFail= "Error! la lección está en blanco"
					return render_to_response('registration/leccionnueva.html', {'profesor':usuario,'error':formFail}, context_instance=RequestContext(request))
				else:
					fecha=datetime.now()
					record=Tips(leccion=leccion, fecha= fecha)
					record.save()

					form = "Tu lección se ha almacenado."
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

		question3=PreguntasVisibles.objects.get(usuario_pendiente=usuario,pregunta=pregunta)
		question3.delete()

		#comprobamos si es correcta
		question2=PreguntasCompletas.objects.get(pregunta=pregunta)

		if respuesta_usuario == question2.respuesta:
			escorrecta=question2.respuesta1_correcta
		elif respuesta_usuario == question2.respuesta2:
			escorrecta=question2.respuesta2_correcta
		elif respuesta_usuario == question2.respuesta3:
			escorrecta=question2.respuesta3_correcta

		#anotamos lo puntos ganados con esta pregunta
		usuario_puntos=Puntuaciones.objects.get(usuario=usuario)
		if escorrecta == "true":
			usuario_puntos.puntos=usuario_puntos.puntos+5
		else:
			usuario_puntos.puntos=usuario_puntos.puntos-1
		usuario_puntos.save()

		#miramos cual era la correcta
		if question2.respuesta1_correcta == "true":
			verdadera=question2.respuesta
		elif question2.respuesta2_correcta == "true":
			verdadera=question2.respuesta2
		elif question2.respuesta3_correcta == "true":
			verdadera=question2.respuesta3

		record=PreguntasRespondidas(usuario_no_pendiente=usuario,pregunta=pregunta,respuesta=verdadera, respuesta_dada=respuesta_usuario, respuesta_usuario_correcta=escorrecta)
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

	user= usuario

	#así selcciono de la base de datos, solo las preguntas dirigidas a los usuarios y los campos que solo necesito para no desvelar las respuestas
	data = serializers.serialize("json", PreguntasVisibles.objects.filter(usuario_pendiente=user), fields=('usuario_pendiente','pregunta', 'respuesta', 'respuesta2', 'respuesta3'))
	return HttpResponse("{\"preguntas\":"+data+"}")

#-------------------------------------------------------------------------------
#Devuelve el listado de las preguntas realizadas
#-------------------------------------------------------------------------------

def androidlistacorrectas(request, usuario):

	user= usuario

	#así selcciono de la base de datos, solo las preguntas dirigidas a los usuarios y los campos que solo necesito para no desvelar las respuestas
	data = serializers.serialize("json", PreguntasRespondidas.objects.filter(usuario_no_pendiente=user), fields=('pregunta', 'respuesta', 'respuesta_dada', 'respuesta_usuario_correcta'))
	return HttpResponse("{\"preguntas\":"+data+"}")

#-------------------------------------------------------------------------------
#devuelve el ranking de alumnos por puntos
#-------------------------------------------------------------------------------

def androidclasificacion(request):

	p=Puntuaciones.objects.all()
	p=p.extra(order_by = ['-puntos'])
	data = serializers.serialize("json",p, fields=('usuario','puntos'))
	return HttpResponse("{\"puntos\":"+data+"}")

#-------------------------------------------------------------------------------
#añade una nueva pregunta para responder al usuario
#-------------------------------------------------------------------------------

def androidsumapregunta(request, usuario):

	user= usuario
	try:
		p = PreguntasPendientes.objects.filter(usuario_pendiente=user)
	
		usuario_pendiente = p[0].usuario_pendiente
		pregunta = p[0].pregunta
		respuesta= p[0].respuesta
		respuesta2= p[0].respuesta2
		respuesta3= p[0].respuesta3
		p[0].delete()


		record=PreguntasVisibles(usuario_pendiente=usuario_pendiente,pregunta=pregunta,respuesta=respuesta,respuesta2=respuesta2, respuesta3=respuesta3)
		record.save()

		#le incrementamos el contador de preguntas obligadas
		pobligada=Puntuaciones.objects.get(usuario=user)
		pobligada.preguntaobligada=pobligada.preguntaobligada+1
		pobligada.save()


		return HttpResponse("ok")
	except:
		return HttpResponse("fail")

#-------------------------------------------------------------------------------
#devuelve el listado de lecciones para los alumnos
#-------------------------------------------------------------------------------

def androidtips(request):

	l=Tips.objects.all()
	l=l.extra(order_by = ['-fecha'])
	data = serializers.serialize("json",l, fields=('leccion'))
	return HttpResponse("{\"tips\":"+data+"}")

#-------------------------------------------------------------------------------
#añade una pregunta extra para responder al usuario y le suma 1 a preguntaextra
#-------------------------------------------------------------------------------

def androidpreguntaextra(request, usuario):

	user= usuario
	try:
		p = PreguntasPendientes.objects.filter(usuario_pendiente=user)
	
		usuario_pendiente = p[0].usuario_pendiente
		pregunta = p[0].pregunta
		respuesta= p[0].respuesta
		respuesta2= p[0].respuesta2
		respuesta3= p[0].respuesta3
		p[0].delete()


		record=PreguntasVisibles(usuario_pendiente=usuario_pendiente,pregunta=pregunta,respuesta=respuesta,respuesta2=respuesta2, respuesta3=respuesta3)
		record.save()

		#le incrementamos el contador de preguntas extras
		pextra=Puntuaciones.objects.get(usuario=user)
		pextra.preguntaextra=pextra.preguntaextra+1
		pextra.save()

		return HttpResponse("ok")
	except:
		return HttpResponse("fail")



			
