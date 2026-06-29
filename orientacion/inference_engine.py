import logging
from typing import Dict, List, Any
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class CalculoInferenciaError(Exception):
    pass

class MotorInferenciaStrategy(ABC):
    @abstractmethod
    def calcular_ranking(self, promedios_alumno: Dict[int, float], especialidades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass

class PromedioPonderadoStrategy(MotorInferenciaStrategy):
    def calcular_ranking(self, promedios_alumno: Dict[int, float], especialidades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not especialidades:
            raise CalculoInferenciaError("La lista de especialidades está vacía.")
            
        ranking: List[Dict[str, Any]] = []
        for esp in especialidades:
            puntaje_afinidad = 0.0
            pesos_totales = 0.0
            
            pesos = esp.get('pesos', [])
            if not pesos:
                raise CalculoInferenciaError(f"La especialidad '{esp.get('nombre', 'Desconocida')}' no tiene pesos configurados.")
                
            for ph in pesos:
                if 'habilidad_id' not in ph:
                    raise CalculoInferenciaError("Estructura de peso inválida: falta 'habilidad_id'.")
                    
                promedio = float(promedios_alumno.get(ph['habilidad_id'], 0.0))
                peso = float(ph.get('peso', 0.0))
                puntaje_afinidad += promedio * peso
                pesos_totales += peso
            
            if pesos_totales <= 0:
                raise CalculoInferenciaError(f"Suma de pesos nula o negativa en la especialidad '{esp.get('nombre', 'Desconocida')}'. División por cero evitada.")
                
            afinidad_final = puntaje_afinidad / pesos_totales
            
            ranking.append({
                'especialidad': esp.get('nombre', ''),
                'area': esp.get('area', ''),
                'afinidad': round(afinidad_final, 1)
            })
            
        return sorted(ranking, key=lambda x: float(x['afinidad']), reverse=True)
