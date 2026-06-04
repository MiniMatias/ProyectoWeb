from django.contrib import admin
from .models import (
    AreaEspecialidad, 
    Especialidad, 
    Estudiante, 
    Habilidad, 
    Pregunta, 
    EspecialidadHabilidad, 
    RespuestaHabilidad
)

# Registro de la estructura base
admin.site.register(AreaEspecialidad)
admin.site.register(Especialidad)
admin.site.register(Estudiante)

# Registro del motor de test
admin.site.register(Habilidad)
admin.site.register(Pregunta)
admin.site.register(EspecialidadHabilidad)
admin.site.register(RespuestaHabilidad)