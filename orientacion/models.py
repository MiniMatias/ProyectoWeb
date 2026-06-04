from django.db import models
from django.core.exceptions import ValidationError

def validar_cedula_ecuatoriana(value):
    if len(value) != 10 or not value.isdigit():
        raise ValidationError('La cédula debe tener 10 dígitos numéricos.')
    provincia = int(value[0:2])
    if provincia < 1 or provincia > 24:
        raise ValidationError('El código de provincia es inválido.')
    
    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = sum(((int(value[i]) * coeficientes[i]) - 9 if (int(value[i]) * coeficientes[i]) > 9 else (int(value[i]) * coeficientes[i])) for i in range(9))
    digito_verificador = ((total + 9) // 10) * 10 - total
    if digito_verificador != int(value[9]):
        raise ValidationError('La cédula ingresada no es matemáticamente válida.')

class AreaEspecialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class Especialidad(models.Model):
    area = models.ForeignKey(AreaEspecialidad, on_delete=models.CASCADE, related_name='especialidades')
    nombre = models.CharField(max_length=100)
    def __str__(self): return f"{self.nombre} ({self.area.nombre})"

class Estudiante(models.Model):
    cedula = models.CharField(max_length=10, unique=True, validators=[validar_cedula_ecuatoriana])
    nombre_completo = models.CharField(max_length=150)
    area_interes = models.ForeignKey(AreaEspecialidad, on_delete=models.SET_NULL, null=True)
    especialidad_especifica = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True)
    def __str__(self): return self.nombre_completo

class Habilidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    def __str__(self): return self.nombre

class Pregunta(models.Model):
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE, related_name='preguntas')
    enunciado = models.TextField()
    def __str__(self): return self.enunciado

class EspecialidadHabilidad(models.Model):
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE, related_name='pesos_habilidades')
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE)
    peso = models.FloatField()

class RespuestaHabilidad(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='respuestas')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    puntaje = models.IntegerField()