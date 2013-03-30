from django.db import models
from django.contrib.auth.models import User

class PreguntasCompletas(models.Model):
	#falta poner el primary key a pregunta para que no se repitan
	#usuario_pendiente=models.TextField()
	pregunta=models.TextField(primary_key=True)
	respuesta=models.TextField()
	respuesta1_correcta=models.TextField()
	respuesta2=models.TextField()
	respuesta2_correcta=models.TextField()
	respuesta3=models.TextField()
	respuesta3_correcta=models.TextField()
	asignatura=models.TextField()

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
	usuario=models.TextField()
	puntos=models.IntegerField()
	preguntaextra=models.IntegerField()
	preguntaobligada=models.IntegerField()
	preguntarecibidaamistosa=models.IntegerField()
	preguntaenviadaamistosa=models.IntegerField()
	asignatura=models.TextField()

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

class CodigosGCM(models.Model):
	usuario=models.TextField()
	codigoGCM=models.TextField()
	asignatura=models.TextField()
	
class Asignaturas(models.Model):
	asignatura=models.TextField()
	profesor=models.TextField()

class AsignaturasAlumno(models.Model):
	asignatura=models.TextField()
	usuario=models.TextField()
	

	

