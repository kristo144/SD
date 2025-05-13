import Pyro4
import threading
import time
import random
from model import InsultService

"""
    Implementación del servicio de insultos usando Pyro4 para su exposición remota.
    Incluye un broadcaster que envía insultos aleatorios a los suscriptores cada 5 segundos.
"""

@Pyro4.expose
class PyroInsultService:


    def __init__(self):
        self.service = InsultService()
        # Iniciar el broadcaster en un hilo separado
        self.running = True
        self.broadcast_thread = threading.Thread(target=self._broadcaster)
        self.broadcast_thread.daemon = True
        self.broadcast_thread.start()

    def add_insult(self, insult):
        """
        Añade un insulto si no existe ya

        Args:
            insult (str): El insulto a añadir

        Returns:
            bool: True si se añadió con éxito, False si ya existía
        """
        return self.service.add_insult(insult)

    def get_insults(self):
        """
        Devuelve la lista completa de insultos

        Returns:
            list: Lista de insultos almacenados
        """
        return self.service.get_insults()

    def subscribe(self, subscriber_id, callback):
        """
        Registra un suscriptor para recibir insultos aleatorios

        Args:
            subscriber_id (str): Identificador único del suscriptor
            callback: Objeto callback para notificar al suscriptor

        Returns:
            bool: True si la suscripción fue exitosa
        """
        return self.service.subscribe(subscriber_id, callback)

    def unsubscribe(self, subscriber_id):
        """
        Elimina un suscriptor de la lista de suscriptores

        Args:
            subscriber_id (str): Identificador único del suscriptor

        Returns:
            bool: True si se eliminó, False si no existía
        """
        return self.service.unsubscribe(subscriber_id)

    def get_subscribers(self):
        """
        Devuelve la lista de IDs de suscriptores

        Returns:
            list: Lista de IDs de suscriptores
        """
        return self.service.get_subscribers()

    def _broadcaster(self):
        """
        Method que se ejecuta en un hilo separado y envía insultos aleatorios
        a los suscriptores cada 5 segundos
        """
        while self.running:
            time.sleep(5)   # pausa de 5 segundos

            # Verificar si hay insultos y suscriptores
            insults = self.service.get_insults()
            if not insults or not self.service.subscribers:
                continue

            # Seleccionar un insulto aleatorio
            random_insult = random.choice(insults)

            # Notificar a todos los suscriptores
            subscribers_to_remove = []
            for subscriber_id, callback in self.service.subscribers.items():
                try:
                    callback.notify(random_insult)
                except Exception:
                    # Si hay error al notificar, eliminar el suscriptor
                    subscribers_to_remove.append(subscriber_id)

            # Eliminar suscriptores con error
            for subscriber_id in subscribers_to_remove:
                self.service.unsubscribe(subscriber_id)


def start_server():
    """
    Inicia el servidor Pyro4 para el servicio de insultos
    """
    insult_service = PyroInsultService() # Crear la instancia del servicio

    # Registrar el servicio con el servidor de nombres
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(insult_service)
    ns.register("insult.service", uri)

    print("InsultService registrado como: insult.service")
    print(f"URI: {uri}")
    print("Servidor iniciado...")

    daemon.requestLoop()    # bucle de eventos


if __name__ == "__main__":
    start_server()