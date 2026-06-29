from django.test import TestCase, Client
from django.urls import reverse
from .models import Estudiante, AreaEspecialidad, Especialidad, Habilidad, Pregunta, EspecialidadHabilidad, RespuestaHabilidad

class DashboardIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.area = AreaEspecialidad.objects.create(nombre="Ingeniería")
        self.especialidad = Especialidad.objects.create(area=self.area, nombre="Sistemas")
        
        # Ignoramos la validación ecuatoriana simulando que ya se guardó
        self.estudiante = Estudiante(cedula="1712345678", nombre_completo="Test", area_interes=self.area, especialidad_especifica=self.especialidad)
        self.estudiante.save()

        self.hab1 = Habilidad.objects.create(nombre="Lógica")
        self.pregunta1 = Pregunta.objects.create(habilidad=self.hab1, enunciado="Q1")
        EspecialidadHabilidad.objects.create(especialidad=self.especialidad, habilidad=self.hab1, peso=1.0)
        
    def test_dashboard_vacio_devuelve_200(self):
        session = self.client.session
        session['estudiante_id'] = self.estudiante.id
        session.save()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orientacion/dashboard_vacio.html')

    def test_dashboard_ejecuta_motor_matematico(self):
        # 1. Creamos respuestas para forzar el cálculo
        RespuestaHabilidad.objects.create(estudiante=self.estudiante, pregunta=self.pregunta1, puntaje=5)
        
        session = self.client.session
        session['estudiante_id'] = self.estudiante.id
        session.save()
        
        # 2. El request debe atravesar la vista, el servicio, y el motor de inferencia exitosamente
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orientacion/dashboard.html')
        
        # 3. Validamos que la matemática pura resolvió y la vista la recibió
        self.assertIn('top_3', response.context)
        self.assertEqual(response.context['top_3'][0]['especialidad'], "Sistemas")
        self.assertEqual(response.context['top_3'][0]['afinidad'], 100.0) # (5-1)*25 = 100% de afinidad