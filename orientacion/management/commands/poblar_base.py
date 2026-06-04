from django.core.management.base import BaseCommand
from django.db import transaction
from orientacion.models import AreaEspecialidad, Especialidad, Habilidad, Pregunta, EspecialidadHabilidad

class Command(BaseCommand):
    help = 'Puebla la base de datos con un catálogo vocacional extenso y calibrado'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando purga de datos anteriores...")
        AreaEspecialidad.objects.all().delete()
        Habilidad.objects.all().delete()

        # 1. CATÁLOGO DE ÁREAS Y ESPECIALIDADES
        estructura_academica = {
            "Ingeniería y Ciencias Aplicadas": ["Ingeniería de Software", "Ciberseguridad", "Ingeniería Industrial"],
            "Ciencias de la Salud": ["Medicina", "Psicología Clínica", "Fisioterapia"],
            "Negocios y Administración": ["Dirección de Empresas", "Marketing Digital", "Finanzas"],
            "Arquitectura y Diseño": ["Diseño Gráfico", "Arquitectura", "Producción Audiovisual"]
        }

        areas_creadas = {}
        especialidades_creadas = {}

        for nombre_area, carreras in estructura_academica.items():
            area = AreaEspecialidad.objects.create(nombre=nombre_area)
            areas_creadas[nombre_area] = area
            for carrera in carreras:
                esp = Especialidad.objects.create(area=area, nombre=carrera)
                especialidades_creadas[carrera] = esp

        # 2. DICCIONARIO DE HABILIDADES Y PREGUNTAS
        # Múltiples preguntas por habilidad reducen el margen de error estadístico.
        banco_preguntas = {
            "Pensamiento Lógico-Matemático": [
                "¿Disfrutas resolviendo problemas matemáticos complejos o acertijos lógicos?",
                "¿Te resulta fácil identificar patrones en series de datos o números?"
            ],
            "Abstracción y Sistemas": [
                "¿Puedes visualizar cómo interactúan las partes de un sistema antes de construirlo?",
                "¿Te gusta desarmar cosas (físicas o de software) para entender cómo funcionan por dentro?"
            ],
            "Inteligencia Interpersonal (Empatía)": [
                "¿Las personas suelen buscarte para contarte sus problemas personales?",
                "¿Puedes percibir fácilmente el estado de ánimo de alguien con solo observarlo?"
            ],
            "Gestión y Liderazgo": [
                "¿Te sientes cómodo tomando el control y delegando tareas en trabajos grupales?",
                "¿Disfrutas organizando eventos, planificando recursos y manejando presupuestos?"
            ],
            "Creatividad y Estética Visual": [
                "¿Notas rápidamente cuando los colores, fuentes o formas no combinan en un diseño?",
                "¿Te gusta expresar tus ideas mediante dibujos, bocetos o herramientas de diseño?"
            ],
            "Precisión y Atención al Detalle": [
                "¿Eres perfeccionista al revisar documentos buscando el más mínimo error ortográfico o de cálculo?",
                "¿Te molesta cuando los procesos no siguen un orden estricto y riguroso?"
            ]
        }

        habilidades_creadas = {}
        for hab_nombre, preguntas in banco_preguntas.items():
            habilidad = Habilidad.objects.create(nombre=hab_nombre)
            habilidades_creadas[hab_nombre] = habilidad
            for enunciado in preguntas:
                Pregunta.objects.create(habilidad=habilidad, enunciado=enunciado)

        # 3. MATRIZ DE PESOS (EL MOTOR DE INFERENCIA)
        # Pesos de 0.0 a 1.0. 
        # 1.0 = Crítico e indispensable. 
        # 0.1 = Irrelevante para la carrera.
        matriz_pesos = {
            "Ingeniería de Software": {
                "Pensamiento Lógico-Matemático": 1.0,
                "Abstracción y Sistemas": 1.0,
                "Precisión y Atención al Detalle": 0.8,
                "Creatividad y Estética Visual": 0.4,
                "Inteligencia Interpersonal (Empatía)": 0.2,
                "Gestión y Liderazgo": 0.5
            },
            "Psicología Clínica": {
                "Inteligencia Interpersonal (Empatía)": 1.0,
                "Gestión y Liderazgo": 0.6,
                "Abstracción y Sistemas": 0.5,
                "Pensamiento Lógico-Matemático": 0.3,
                "Creatividad y Estética Visual": 0.3,
                "Precisión y Atención al Detalle": 0.6
            },
            "Diseño Gráfico": {
                "Creatividad y Estética Visual": 1.0,
                "Abstracción y Sistemas": 0.7,
                "Inteligencia Interpersonal (Empatía)": 0.6,
                "Precisión y Atención al Detalle": 0.8,
                "Pensamiento Lógico-Matemático": 0.2,
                "Gestión y Liderazgo": 0.3
            },
            "Dirección de Empresas": {
                "Gestión y Liderazgo": 1.0,
                "Pensamiento Lógico-Matemático": 0.7,
                "Inteligencia Interpersonal (Empatía)": 0.8,
                "Abstracción y Sistemas": 0.6,
                "Precisión y Atención al Detalle": 0.7,
                "Creatividad y Estética Visual": 0.4
            }
        }

        # Generación relacional de la matriz
        for carrera, pesos in matriz_pesos.items():
            especialidad_obj = especialidades_creadas.get(carrera)
            if especialidad_obj:
                for hab_nombre, valor_peso in pesos.items():
                    hab_obj = habilidades_creadas.get(hab_nombre)
                    EspecialidadHabilidad.objects.create(
                        especialidad=especialidad_obj,
                        habilidad=hab_obj,
                        peso=valor_peso
                    )

        self.stdout.write(self.style.SUCCESS("Base de datos poblada exitosamente. Matriz de pesos inyectada."))