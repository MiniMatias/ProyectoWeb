from django.contrib import admin
from .models import AreaEspecialidad, Especialidad, Estudiante, Materia, EspecialidadMateria, Nota, Habilidad, EspecialidadHabilidad, Pregunta, RespuestaHabilidad

admin.site.register(AreaEspecialidad)
admin.site.register(Especialidad)
admin.site.register(Estudiante)
admin.site.register(Materia)
admin.site.register(EspecialidadMateria)
admin.site.register(Nota)
admin.site.register(Habilidad)
admin.site.register(EspecialidadHabilidad)
admin.site.register(Pregunta)
admin.site.register(RespuestaHabilidad)