#!/usr/bin/env python3
# InsultService implementación con PyRO4

import random
import time
import threading
import Pyro4
from typing import List


@Pyro4.expose
class InsultService(object):
    """
    Servicio que almacena insultos y permite emitir insultos aleatorios a suscriptores.
    """

    def __init__(self):
        self._insults = [   # Lista de insultos
            "cabeza hueca",
            "torpe",
            "payaso sin gracia",
            "inútil crónico",
            "memo",
            "chapucero",
            "incompetente",
            "caradura",
            "vago incorregible",
            "cateto",
            "clueless",
            "code monkey",
            "lazy bum",
            "you fool",
            "rookie mistake",
            "bug lover",
            "script kiddie",
            "wannabe hacker",
            "brain dead",
            "sloppy coder"
        ]
        self._subscribers = []  # Lista de callbacks a suscriptores
        self._broadcaster_thread = None
        self._running = False

        # Iniciar el broadcaster en un hilo separado
        self.start_broadcaster()

    def add_insult(self, insult):
        """
        Añade un insulto a la lista si no existe ya.

        Args:
            insult: El insulto a añadir

        Returns:
            bool: True si se añadió correctamente, False si ya existía
        """
        if insult in self._insults:
            return False

        self._insults.append(insult)
        return True

    def get_insults(self):
        """
        Devuelve la lista completa de insultos.

        Returns:
            List[str]: Lista de insultos
        """
        return self._insults

    def subscribe(self, callback):
        """
        Registra un callback para recibir notificaciones de insultos aleatorios.

        Args:
            callback: Objeto callback remoto que implementa un method 'notify'
        """
        print(f"Nuevo suscriptor registrado: {callback}")
        self._subscribers.append(callback)
        return True

    def unsubscribe(self, callback):
        """
        Elimina un callback de la lista de suscriptores.

        Args:
            callback: El callback a eliminar
        """
        if callback in self._subscribers:
            self._subscribers.remove(callback)
            return True
        return False

    def _broadcast_random_insult(self):
        """
        Envía un insulto aleatorio a todos los suscriptores.
        """
        if not self._insults:
            return

        # Seleccionar un insulto aleatorio
        random_insult = random.choice(self._insults)

        # Notificar a los suscriptores
        dead_subscribers = []
        for subscriber in self._subscribers:
            try:
                subscriber.notify(random_insult)
            except Exception as e:
                print(f"Error al notificar al suscriptor: {e}")
                dead_subscribers.append(subscriber)

        # Eliminar suscriptores muertos
        for dead in dead_subscribers:
            if dead in self._subscribers:
                self._subscribers.remove(dead)

    def _broadcaster_loop(self):
        """
        Bucle que emite un insulto aleatorio cada 5 segundos.
        """
        while self._running:
            self._broadcast_random_insult()
            time.sleep(5)  # Dormir durante 5 segundos

    def start_broadcaster(self):
        """
        Inicia el hilo broadcaster si no está ya en ejecución.
        """
        if self._broadcaster_thread is None or not self._broadcaster_thread.is_alive():
            self._running = True
            self._broadcaster_thread = threading.Thread(target=self._broadcaster_loop)
            self._broadcaster_thread.daemon = True
            self._broadcaster_thread.start()

    def stop_broadcaster(self):
        """
        Detiene el hilo broadcaster.
        """
        self._running = False
        if self._broadcaster_thread:
            self._broadcaster_thread.join(timeout=1.0)
            self._broadcaster_thread = None


# Implementación del callback para los suscriptores
@Pyro4.expose
class InsultSubscriber(object):
    def __init__(self, name):
        self.name = name
        self.received_insults = []

    def notify(self, insult):
        print(f"[{self.name}] Recibido: {insult}")
        self.received_insults.append(insult)
        return True


def main():
    # Configurar el servidor
    Pyro4.config.SERVERTYPE = "multiplex"  # Tipo de servidor para manejar múltiples clientes

    # Crear y registrar el servicio InsultService
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()

    service = InsultService()
    uri = daemon.register(service)
    ns.register("insult.service", uri)

    print(f"InsultService listo. URI: {uri}")
    daemon.requestLoop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Servidor detenido por el usuario")