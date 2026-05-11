from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

def validar_cedula_ecuatoriana(cedula):
    if not cedula or not cedula.isdigit() or len(cedula) != 10:
        raise ValidationError('La cédula debe tener exactamente 10 dígitos numéricos.')
    
    provincia = int(cedula[0:2])
    if provincia < 1 or provincia > 24:
        raise ValidationError('El código de provincia es inválido.')

    tercer_digito = int(cedula[2])
    if tercer_digito > 5:
        raise ValidationError('El tercer dígito es inválido para personas naturales.')

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    total = 0
    for i in range(9):
        valor = int(cedula[i]) * coeficientes[i]
        total += valor if valor < 10 else valor - 9

    digito_verificador = int(cedula[9])
    decena_superior = ((total // 10) + 1) * 10
    resultado = decena_superior - total
    if resultado == 10:
        resultado = 0

    if resultado != digito_verificador:
        raise ValidationError('La cédula ingresada no es matemáticamente válida.')

class AreaEspecialidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre

class Especialidad(models.Model):
    area = models.ForeignKey(AreaEspecialidad, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.nombre} ({self.area.nombre})"

class Estudiante(models.Model):
    cedula = models.CharField(max_length=10, unique=True)
    nombre_completo = models.CharField(max_length=200)
    area_interes = models.ForeignKey(AreaEspecialidad, on_delete=models.SET_NULL, null=True)
    especialidad_especifica = models.ForeignKey(Especialidad, on_delete=models.SET_NULL, null=True)

    def clean(self):
        super().clean()
        # Validación Crítica en Back-End
        if self.cedula:
            validar_cedula_ecuatoriana(self.cedula)

        # Evitar inconsistencias de base de datos
        if self.area_interes and self.especialidad_especifica:
            if self.especialidad_especifica.area != self.area_interes:
                raise ValidationError('La especialidad no pertenece al área seleccionada.')

    def save(self, *args, **kwargs):
        self.full_clean() # Fuerza la validación antes de cualquier guardado
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_completo
class Materia(models.Model):
    codigo = models.CharField(max_length=20, unique=True, help_text="Ej: PRG-101")
    nombre = models.CharField(max_length=150)
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class EspecialidadMateria(models.Model):
    """
    Tabla intermedia vital. Define cuánto "pesa" una materia específica 
    para una especialidad en particular. 
    Ejemplo: Base de Datos pesa 1.0 para 'Backend', pero 0.3 para 'Frontend'.
    """
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE, related_name='pesos_materias')
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    peso = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Valor ponderado entre 0.0 y 1.0"
    )

    class Meta:
        # Una materia solo puede tener un peso definido por especialidad
        unique_together = ('especialidad', 'materia')

    def __str__(self):
        return f"{self.materia.nombre} -> {self.especialidad.nombre} (Peso: {self.peso})"

class Nota(models.Model):
    """
    El registro histórico del estudiante.
    """
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='notas')
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE)
    calificacion = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(10.0)],
        help_text="Calificación sobre 10"
    )

    class Meta:
        # Un estudiante no debería tener dos notas finales para la misma materia en este modelo base
        unique_together = ('estudiante', 'materia')

    def __str__(self):
        return f"{self.estudiante.nombre_completo} - {self.materia.nombre}: {self.calificacion}"
    
class Habilidad(models.Model):
    nombre = models.CharField(max_length=100, unique=True, help_text="Ej: Lógica Algorítmica, Análisis de Datos, Redes")
    
    def __str__(self):
        return self.nombre

class EspecialidadHabilidad(models.Model):
    """
    Define cuánto importa una habilidad para una especialidad.
    Ej: 'Lógica Algorítmica' pesa 1.0 para Backend, pero 0.4 para UX/UI.
    """
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE, related_name='pesos_habilidades')
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE)
    peso = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="Peso de la habilidad entre 0.0 y 1.0"
    )

    class Meta:
        unique_together = ('especialidad', 'habilidad')

    def __str__(self):
        return f"{self.habilidad.nombre} -> {self.especialidad.nombre} (Peso: {self.peso})"

class Pregunta(models.Model):
    habilidad = models.ForeignKey(Habilidad, on_delete=models.CASCADE, related_name='preguntas')
    enunciado = models.TextField()
    
    def __str__(self):
        return f"[{self.habilidad.nombre}] {self.enunciado[:50]}..."

class RespuestaHabilidad(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name='respuestas_habilidades')
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    # Escala de Likert: 1 (Totalmente en desacuerdo) a 5 (Totalmente de acuerdo)
    puntaje = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('estudiante', 'pregunta') # Un estudiante responde una pregunta solo una vez

    def __str__(self):
        return f"{self.estudiante.cedula} - {self.pregunta.id}: {self.puntaje}"
    