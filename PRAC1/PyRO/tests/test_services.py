import unittest
import sys
import os
import time
import threading
import uuid
import Pyro4

# Añadir el directorio raíz al path para importaciones relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ..insult_service.model import InsultService
from ..insult_filter.model import InsultFilter


# Implementación simple de callback para pruebas
@Pyro4.expose
class TestCallback:
    def __init__(self):
        self.notifications = []

    def notify(self, insult):
        self.notifications.append(insult)
        return True


class TestInsultService(unittest.TestCase):
    """
    Pruebas unitarias para el servicio de insultos
    """

    def setUp(self):
        """Configuración previa a cada prueba"""
        self.service = InsultService()

    def test_add_insult(self):
        """Prueba añadir un insulto"""
        # Añadir un insulto
        result = self.service.add_insult("tonto")
        self.assertTrue(result)
        self.assertIn("tonto", self.service.get_insults())

        # Probar añadir el mismo insulto (debería fallar)
        result = self.service.add_insult("tonto")
        self.assertFalse(result)

        # Probar añadir un insulto vacío (debería fallar)
        result = self.service.add_insult("")
        self.assertFalse(result)

        # Probar añadir un insulto con espacios
        result = self.service.add_insult("  ")
        self.assertFalse(result)

    def test_get_insults(self):
        """Prueba obtener la lista de insultos"""
        # Inicialmente vacía
        self.assertEqual(self.service.get_insults(), [])

        # Añadir algunos insultos
        self.service.add_insult("tonto")
        self.service.add_insult("idiota")

        # Verificar que se devuelven correctamente
        insults = self.service.get_insults()
        self.assertEqual(len(insults), 2)
        self.assertIn("tonto", insults)
        self.assertIn("idiota", insults)

    def test_subscribe_unsubscribe(self):
        """Prueba la suscripción y cancelación"""
        # Crear un callback
        callback = TestCallback()

        # Suscribir
        subscriber_id = str(uuid.uuid4())
        result = self.service.subscribe(subscriber_id, callback)
        self.assertTrue(result)
        self.assertIn(subscriber_id, self.service.get_subscribers())

        # Cancelar suscripción
        result = self.service.unsubscribe(subscriber_id)
        self.assertTrue(result)
        self.assertNotIn(subscriber_id, self.service.get_subscribers())

        # Cancelar suscripción inexistente
        result = self.service.unsubscribe("nonexistent")
        self.assertFalse(result)


class TestInsultFilter(unittest.TestCase):
    """
    Pruebas unitarias para el servicio de filtrado
    """

    def setUp(self):
        """Configuración previa a cada prueba"""
        self.filter = InsultFilter()

    def test_filter_text(self):
        """Prueba el filtrado de texto"""
        # Lista de insultos para filtrar
        insults = ["tonto", "idiota"]

        # Probar filtrado básico
        text = "Eres un tonto y un idiota"
        filtered = self.filter.filter_text(text, insults)
        self.assertEqual(filtered, "Eres un CENSORED y un CENSORED")

        # Probar filtrado con mayúsculas/minúsculas
        text = "Eres un TONTO y un Idiota"
        filtered = self.filter.filter_text(text, insults)
        self.assertEqual(filtered, "Eres un CENSORED y un CENSORED")

        # Probar texto sin insultos
        text = "Hola mundo"
        filtered = self.filter.filter_text(text, insults)
        self.assertEqual(filtered, "Hola mundo")

        # Verificar que los textos filtrados se almacenan
        self.assertEqual(len(self.filter.get_filtered_texts()), 3)

    def test_get_filtered_texts(self):
        """Prueba obtener la lista de textos filtrados"""
        # Inicialmente vacía
        self.assertEqual(self.filter.get_filtered_texts(), [])

        # Añadir algunos textos filtrados
        self.filter.filter_text("Texto 1 con tonto", ["tonto"])
        self.filter.filter_text("Texto 2 sin insultos", ["tonto"])

        # Verificar que se devuelven correctamente
        filtered_texts = self.filter.get_filtered_texts()
        self.assertEqual(len(filtered_texts), 2)
        self.assertEqual(filtered_texts[0], "Texto 1 con CENSORED")
        self.assertEqual(filtered_texts[1], "Texto 2 sin insultos")


def run_tests():
    """Ejecutar todas las pruebas unitarias"""
    unittest.main()


if __name__ == "__main__":
    run_tests()