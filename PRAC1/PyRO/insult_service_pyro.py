# insult_service_pyro.py
import Pyro4
import random
import threading
import time


@Pyro4.expose
class InsultService:
    def __init__(self):
        self.insults = []  # Lista para almacenar los insultos
        self.subscribers = []  # Lista para almacenar los suscriptores
        # Iniciar el hilo para transmitir insultos periódicamente
        self.broadcast_thread = threading.Thread(target=self._broadcast_insults)
        self.broadcast_thread.daemon = True
        self.broadcast_thread.start()

    def add_insult(self, insult):
        """Añade un insulto a la lista si no existe ya"""
        if insult not in self.insults:
            self.insults.append(insult)
            return True
        return False

    def get_insults(self):
        """Devuelve la lista completa de insultos"""
        return self.insults

    def subscribe(self, subscriber_uri):
        """Permite a los clientes suscribirse para recibir insultos aleatorios"""
        if subscriber_uri not in self.subscribers:
            self.subscribers.append(subscriber_uri)
            return True
        return False

    def unsubscribe(self, subscriber_uri):
        """Permite a los clientes cancelar su suscripción"""
        if subscriber_uri in self.subscribers:
            self.subscribers.remove(subscriber_uri)
            return True
        return False

    def _broadcast_insults(self):
        """Método privado que envía un insulto aleatorio a todos los suscriptores cada 5 segundos"""
        while True:
            time.sleep(5)  # Esperar 5 segundos entre transmisiones
            if self.insults and self.subscribers:  # Verificar que haya insultos y suscriptores
                random_insult = random.choice(self.insults)
                # Notificar a todos los suscriptores
                for subscriber_uri in self.subscribers[:]:  # Copiar la lista para evitar problemas de concurrencia
                    try:
                        subscriber = Pyro4.Proxy(subscriber_uri)
                        subscriber.receive_insult(random_insult)
                    except Exception as e:
                        print(f"Error al notificar al suscriptor {subscriber_uri}: {e}")
                        # Eliminar el suscriptor que falló
                        self.subscribers.remove(subscriber_uri)


# Iniciar el servidor Pyro4
def start_server():
    # Crear y registrar el servicio
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(InsultService)
    ns.register("insult.service", uri)

    print(f"El servidor InsultService está ejecutándose en: {uri}")
    daemon.requestLoop()


if __name__ == "__main__":
    start_server()