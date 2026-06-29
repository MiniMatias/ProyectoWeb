import unittest
from typing import Dict, List, Any
from .inference_engine import PromedioPonderadoStrategy, CalculoInferenciaError

class TestPromedioPonderadoStrategy(unittest.TestCase):
    def setUp(self) -> None:
        self.strategy = PromedioPonderadoStrategy()

    def test_especialidades_vacias(self):
        with self.assertRaisesRegex(CalculoInferenciaError, "La lista de especialidades está vacía."):
            self.strategy.calcular_ranking({}, [])

    def test_especialidad_sin_pesos(self):
        especialidades = [{'nombre': 'Ingeniería', 'pesos': []}]
        with self.assertRaisesRegex(CalculoInferenciaError, "no tiene pesos configurados"):
            self.strategy.calcular_ranking({}, especialidades)

    def test_peso_sin_habilidad_id(self):
        especialidades = [{'nombre': 'Ingeniería', 'pesos': [{'peso': 1.0}]}]
        with self.assertRaisesRegex(CalculoInferenciaError, "falta 'habilidad_id'"):
            self.strategy.calcular_ranking({}, especialidades)

    def test_division_por_cero(self):
        especialidades = [{'nombre': 'Arte', 'pesos': [{'habilidad_id': 1, 'peso': 0.0}]}]
        with self.assertRaisesRegex(CalculoInferenciaError, "Suma de pesos nula o negativa"):
            self.strategy.calcular_ranking({}, especialidades)
            
    def test_calculo_exitoso(self):
        promedios = {1: 80.0, 2: 90.0}
        especialidades = [
            {
                'nombre': 'Ingeniería', 
                'area': 'Ciencias',
                'pesos': [
                    {'habilidad_id': 1, 'peso': 1.0}, 
                    {'habilidad_id': 2, 'peso': 2.0}
                ]
            }
        ]
        
        resultado = self.strategy.calcular_ranking(promedios, especialidades)
        
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]['especialidad'], 'Ingeniería')
        self.assertEqual(resultado[0]['area'], 'Ciencias')
        # (80*1 + 90*2) / 3 = 260 / 3 = 86.66...
        self.assertEqual(resultado[0]['afinidad'], 86.7)
