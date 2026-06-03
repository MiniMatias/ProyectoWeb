from django.core.management.base import BaseCommand
from orientacion.models import AreaEspecialidad, Especialidad, Habilidad, Pregunta, EspecialidadHabilidad

class Command(BaseCommand):
    help = 'Puebla la base de datos con la matriz del motor de inferencia'

    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando inyección de datos relacionales...')

        # 1. Catálogo Base
        area, _ = AreaEspecialidad.objects.get_or_create(nombre='Ingeniería y Tecnología')

        # 2. Especialidades
        software, _ = Especialidad.objects.get_or_create(area=area, nombre='Ingeniería de Software')
        ciber, _ = Especialidad.objects.get_or_create(area=area, nombre='Ciberseguridad')
        datos, _ = Especialidad.objects.get_or_create(area=area, nombre='Ciencia de Datos')

        # 3. Habilidades
        hab_logica, _ = Habilidad.objects.get_or_create(nombre='Lógica Algorítmica')
        hab_mate, _ = Habilidad.objects.get_or_create(nombre='Razonamiento Matemático')
        hab_estruc, _ = Habilidad.objects.get_or_create(nombre='Análisis Estructural')
        hab_riesgo, _ = Habilidad.objects.get_or_create(nombre='Gestión de Riesgos')

        # 4. Banco de Preguntas
        preguntas = [
            (hab_logica, 'Me resulta natural dividir un problema grande en pasos pequeños y secuenciales.'),
            (hab_logica, 'Disfruto encontrando la forma más rápida y eficiente de completar una tarea repetitiva.'),
            (hab_mate, 'Tengo facilidad para el álgebra abstracta y el cálculo modular.'),
            (hab_mate, 'Puedo interpretar fácilmente información estadística o métricas en tablas complejas.'),
            (hab_estruc, 'Me interesa entender cómo se conectan las distintas partes de un sistema (como una red de computadoras o un motor).'),
            (hab_estruc, 'Cuando un aparato electrónico falla, mi primer instinto es desarmarlo para rastrear el origen del problema.'),
            (hab_riesgo, 'Soy meticuloso al buscar posibles fallas de seguridad o vulnerabilidades en las reglas de un juego o sistema.'),
            (hab_riesgo, 'Prefiero trabajar bajo normativas estrictas y protocolos de seguridad antes que improvisar soluciones.'),
        ]

        for habilidad, enunciado in preguntas:
            Pregunta.objects.get_or_create(habilidad=habilidad, enunciado=enunciado)

        # 5. La Matriz de Varianza (Pesos)
        pesos = [
            # Software
            (software, hab_logica, 1.0),
            (software, hab_estruc, 0.8),
            (software, hab_mate, 0.6),
            (software, hab_riesgo, 0.4),
            # Ciberseguridad
            (ciber, hab_riesgo, 1.0),
            (ciber, hab_estruc, 0.9),
            (ciber, hab_logica, 0.5),
            (ciber, hab_mate, 0.5),
            # Ciencia de Datos
            (datos, hab_mate, 1.0),
            (datos, hab_logica, 0.9),
            (datos, hab_estruc, 0.4),
            (datos, hab_riesgo, 0.3),
        ]

        for especialidad, habilidad, peso in pesos:
            EspecialidadHabilidad.objects.update_or_create(
                especialidad=especialidad, 
                habilidad=habilidad,
                defaults={'peso': peso}
            )

        self.stdout.write(self.style.SUCCESS('Base de datos poblada con éxito. Matriz matemática lista.'))