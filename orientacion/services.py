import logging
from typing import List, Dict, Any, Tuple
from django.core.exceptions import ValidationError
from django.core.cache import cache
from .models import Estudiante, AreaEspecialidad, Especialidad, Pregunta, RespuestaHabilidad
from .inference_engine import MotorInferenciaStrategy, CalculoInferenciaError

logger = logging.getLogger(__name__)

class RegistroService:
    @staticmethod
    def registrar_estudiante(cedula: str, nombre_completo: str, area_id: str, especialidad_id: str) -> Estudiante:
        try:
            area_obj = AreaEspecialidad.objects.get(id=area_id)
            especialidad_obj = Especialidad.objects.get(id=especialidad_id)
        except (AreaEspecialidad.DoesNotExist, Especialidad.DoesNotExist):
            raise ValidationError("El área o especialidad seleccionada no existe en el sistema.")

        nuevo_estudiante = Estudiante(
            cedula=cedula,
            nombre_completo=nombre_completo,
            area_interes=area_obj,
            especialidad_especifica=especialidad_obj
        )
        nuevo_estudiante.full_clean()
        nuevo_estudiante.save()
        return nuevo_estudiante

class TestVocacionalService:
    @staticmethod
    def guardar_respuestas(estudiante: Estudiante, datos_respuestas: Dict[int, int]) -> None:
        preguntas_ids = datos_respuestas.keys()
        preguntas = Pregunta.objects.filter(id__in=preguntas_ids)
        
        respuestas_a_crear = [
            RespuestaHabilidad(estudiante=estudiante, pregunta=p, puntaje=datos_respuestas[p.id])
            for p in preguntas if p.id in datos_respuestas
        ]
        
        if respuestas_a_crear:
            # Eliminamos anteriores para permitir reintentos sin duplicar IDs
            RespuestaHabilidad.objects.filter(estudiante=estudiante).delete()
            RespuestaHabilidad.objects.bulk_create(respuestas_a_crear)

class EstudianteDashboardService:
    def __init__(self, motor_inferencia: MotorInferenciaStrategy):
        self.motor_inferencia = motor_inferencia

    def procesar_dashboard(self, estudiante: Estudiante) -> Dict[str, Any]:
        respuestas = RespuestaHabilidad.objects.filter(estudiante=estudiante).select_related('pregunta__habilidad')
        
        if not respuestas.exists():
            return {'vacio': True}
            
        labels, data_points, promedios_dto = self._preparar_datos_graficos_y_promedios(respuestas)
        especialidades_dto = self._obtener_dto_especialidades_cacheado()
        
        try:
            ranking = self.motor_inferencia.calcular_ranking(promedios_dto, especialidades_dto)
            return {
                'vacio': False,
                'labels': labels,
                'data_points': data_points,
                'top_3': ranking[:3]
            }
        except CalculoInferenciaError as e:
            # Ahora sí diagnosticamos el error antes de silenciarlo
            logger.error(f"Fallo matemático en dashboard para estudiante ID {estudiante.id}: {str(e)}")
            return {
                'vacio': False,
                'labels': labels,
                'data_points': data_points,
                'error_inferencia': True
            }

    def _preparar_datos_graficos_y_promedios(self, respuestas) -> Tuple[List[str], List[float], Dict[int, float]]:
        habilidades_data = {}
        promedios_estudiante = {}
        
        for r in respuestas:
            hab_nombre = r.pregunta.habilidad.nombre
            hab_id = r.pregunta.habilidad.id
            porcentaje = (r.puntaje - 1) * 25

            if hab_nombre not in habilidades_data:
                habilidades_data[hab_nombre] = {'suma': 0, 'conteo': 0}
            if hab_id not in promedios_estudiante:
                promedios_estudiante[hab_id] = {'suma': 0, 'conteo': 0}
            
            habilidades_data[hab_nombre]['suma'] += porcentaje
            habilidades_data[hab_nombre]['conteo'] += 1
            promedios_estudiante[hab_id]['suma'] += porcentaje
            promedios_estudiante[hab_id]['conteo'] += 1
            
        labels = list(habilidades_data.keys())
        data_points = [round(data['suma'] / data['conteo'], 1) for data in habilidades_data.values()]
        promedios_dto = {h_id: vals['suma']/vals['conteo'] for h_id, vals in promedios_estudiante.items()}
        
        return labels, data_points, promedios_dto

    def _obtener_dto_especialidades_cacheado(self) -> List[Dict[str, Any]]:
        # Previene la serialización O(N) masiva de la base de datos en cada request
        cache_key = 'orientacion_especialidades_dto'
        dto = cache.get(cache_key)
        
        if not dto:
            todas = Especialidad.objects.select_related('area').prefetch_related('pesos_habilidades__habilidad')
            dto = []
            for esp in todas:
                pesos = [{'habilidad_id': ph.habilidad.id, 'peso': ph.peso} for ph in esp.pesos_habilidades.all()]
                dto.append({'nombre': esp.nombre, 'area': esp.area.nombre, 'pesos': pesos})
            cache.set(cache_key, dto, timeout=86400) # Caché de 24 horas
            
        return dto
