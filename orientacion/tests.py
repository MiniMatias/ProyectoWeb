from django.test import TestCase
from django.urls import reverse
from orientacion.models import Estudiante, AreaEspecialidad, Especialidad, Habilidad, Pregunta, EspecialidadHabilidad

class MotorInferenciaTests(TestCase):
    def setUp(self):
        """
        Esta función se ejecuta ANTES de cada prueba.
        Crea un ecosistema de laboratorio aislado en la memoria RAM.
        """
        # 1. Crear el catálogo base
        self.area = AreaEspecialidad.objects.create(nombre="Tecnología")
        self.especialidad_software = Especialidad.objects.create(area=self.area, nombre="Software")
        
        # 2. Crear las habilidades y preguntas
        self.hab_logica = Habilidad.objects.create(nombre="Lógica")
        self.pregunta_1 = Pregunta.objects.create(habilidad=self.hab_logica, enunciado="¿Te gusta programar?")
        self.pregunta_2 = Pregunta.objects.create(habilidad=self.hab_logica, enunciado="¿Resuelves algoritmos?")
        
        # 3. Crear la matriz de pesos
        EspecialidadHabilidad.objects.create(
            especialidad=self.especialidad_software,
            habilidad=self.hab_logica,
            peso=1.0 # Peso máximo
        )
        
        # 4. Registrar un estudiante fantasma que CUMPLE con validaciones
        self.estudiante = Estudiante.objects.create(
            cedula="1712345675", # Cédula matemáticamente válida (Módulo 10 verificado)
            nombre_completo="Estudiante Bot de Pruebas",
            area_interes=self.area,
            especialidad_especifica=self.especialidad_software
        )

    def test_calculo_afinidad_maxima(self):
        """
        Simula a un estudiante respondiendo '5' (Totalmente Capaz) a todas las preguntas.
        El algoritmo DEBE devolver exactamente 100.0% de afinidad.
        """
        session = self.client.session
        session['estudiante_id'] = self.estudiante.id
        session.save()

        datos_formulario = {
            f'pregunta_{self.pregunta_1.id}': '5',
            f'pregunta_{self.pregunta_2.id}': '5',
        }
        
        response = self.client.post(reverse('realizar_test'), datos_formulario)
        
        self.assertEqual(response.status_code, 200)
        
        resultados = response.context.get('resultados', [])
        
        self.assertTrue(len(resultados) > 0, "No se generaron resultados de afinidad.")
        
        resultado_software = resultados[0]
        self.assertEqual(resultado_software['especialidad'], "Software")
        self.assertEqual(resultado_software['afinidad'], 100.0)