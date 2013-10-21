from django.db import models
from django.contrib.auth.models import User

class Persona(models.Model):
    usuario = models.OneToOneField(User)
    colegio = models.TextField()
    nombreyapellidos=models.TextField()

class PreguntasCompletas(models.Model):
	pregunta=models.TextField()
	respuesta=models.TextField()
	respuesta1_correcta=models.TextField()
	respuesta2=models.TextField()
	respuesta2_correcta=models.TextField()
	respuesta3=models.TextField()
	respuesta3_correcta=models.TextField()
	asignatura=models.TextField()
	colegio=models.TextField()

class PreguntasPendientes(models.Model):
	usuario_pendiente=models.TextField()
	pregunta=models.TextField()
	respuesta=models.TextField()
	respuesta2=models.TextField()
	respuesta3=models.TextField()
	asignatura=models.TextField()

class PreguntasRespondidas(models.Model):
	usuario_no_pendiente=models.TextField()
	pregunta=models.TextField()
	respuesta=models.TextField()
	respuesta_dada=models.TextField()
	respuesta_usuario_correcta=models.TextField()
	fecha=models.DateTimeField()
	asignatura=models.TextField()


class Puntuaciones(models.Model):
	#por cada asignatura
	usuario=models.TextField()
	puntos=models.IntegerField()
	preguntaextra=models.IntegerField()
	preguntaobligada=models.IntegerField()
	preguntarecibidaamistosa=models.IntegerField()
	preguntaenviadaamistosa=models.IntegerField()
	asignatura=models.TextField()
	colegio=models.TextField()
	npreguntasincorrectas=models.IntegerField()
	npreguntascorrectas=models.IntegerField()


class PreguntasVisibles(models.Model):
	usuario_pendiente=models.TextField()
	pregunta=models.TextField()
	respuesta=models.TextField()
	respuesta2=models.TextField()
	respuesta3=models.TextField()
	#puede ser: obligada, extra, amistosa
	tag=models.TextField()
	asignatura=models.TextField()

class Tips(models.Model):
	leccion=models.TextField()
	fecha=models.DateTimeField()
	asignatura=models.TextField()
	colegio=models.TextField()

class CodigosGCM(models.Model):
	usuario=models.TextField()
	codigoGCM=models.TextField()

class Asignaturas(models.Model):
	#se pueden repetir asignaturas pero en distintos colegios
	asignatura=models.TextField()
	profesor=models.TextField()
	colegio=models.TextField()

class AsignaturasAlumno(models.Model):
	asignatura=models.TextField()
	usuario=models.TextField()
	
class Colegios(models.Model):
	colegio=models.TextField()

class MedidaOcioDiaria(models.Model):
	#no depende de asignatura ya que es para aproximar el tiempo
	usuario=models.TextField()
	nPreguntasdia=models.IntegerField()
	fecha=models.DateField()
	
class Comentarios(models.Model):
	usuario=models.TextField()
	fecha=models.DateTimeField()
	asignatura=models.TextField()
	colegio=models.TextField()
	comentario=models.TextField()

