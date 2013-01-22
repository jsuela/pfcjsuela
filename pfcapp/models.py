from django.db import models
from django.contrib.auth.models import User

class PreguntasCompletas(models.Model):
	#falta poner el primary key a pregunta para que no se repitan
	#usuario_pendiente=models.TextField()
	pregunta=models.TextField()
	respuesta=models.TextField()
	respuesta1_correcta=models.TextField()
	respuesta2=models.TextField()
	respuesta2_correcta=models.TextField()
	respuesta3=models.TextField()
	respuesta3_correcta=models.TextField()

class PreguntasPendientes(models.Model):
	usuario_pendiente=models.TextField()
	pregunta=models.TextField()
	respuesta=models.TextField()
	respuesta2=models.TextField()
	respuesta3=models.TextField()

class PreguntasRespondidas(models.Model):
	usuario_no_pendiente=models.TextField()
	pregunta=models.TextField()
	respuesta=models.TextField()
	respuesta_dada=models.TextField()
	respuesta_usuario_correcta=models.TextField()

class Puntuaciones(models.Model):
	usuario=models.TextField()
	puntos=models.IntegerField()
	preguntaextra=models.IntegerField()
	preguntaobligada=models.IntegerField()

class PreguntasVisibles(models.Model):
	usuario_pendiente=models.TextField()
	pregunta=models.TextField()
	respuesta=models.TextField()
	respuesta2=models.TextField()
	respuesta3=models.TextField()

class Tips(models.Model):
	leccion=models.TextField()
	fecha=models.DateTimeField()

	

