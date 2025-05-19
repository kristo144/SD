import Pyro4
import Pyro4.errors
import threading
import time
import random
import sys
import os
import socket

# Añadir el directorio raíz al path para importaciones relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar el modelo original
from model import InsultService

"""
    Implementación modificada del servicio de insultos usando Pyro4 para su exposición remota.
    Esta versión está diseñada para trabajar con el sistema de balanceo de carga.
"""

@Pyro4.expose
class PyroInsultService:
    def __init__(self, server_id=None):
        self.service = InsultService()
        self.server_id = server_id or socket.gethostname()
        # Iniciar el broadcaster en un hilo separado
        self.running = True
        self.broadcast_thread = threading.Thread(target=self._broadcaster)
        self.broadcast_thread.daemon = True
        self.broadcast_thread.start()
        
        # Para sincronización con el balanceador de carga
        self.registered_with_balancer = False
        self.balancer_uri = None

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
        # En esta versión, las suscripciones son gestionadas por el balanceador
        # Pero aún implementamos el method para mantener compatibilidad
        try:
            if self.balancer_uri:
                balancer = Pyro4.Proxy(self.balancer_uri)
                return balancer.subscribe(subscriber_id, callback)
        except Pyro4.errors.PyroError:
            pass
        
        return self.service.subscribe(subscriber_id, callback)

    def unsubscribe(self, subscriber_id):
        """
        Elimina un suscriptor de la lista de suscriptores

        Args:
            subscriber_id (str): Identificador único del suscriptor

        Returns:
            bool: True si se eliminó, False si no existía
        """
        # En esta versión, las suscripciones son gestionadas por el balanceador
        # Pero aún implementamos el method para mantener compatibilidad
        try:
            if self.balancer_uri:
                balancer = Pyro4.Proxy(self.balancer_uri)
                return balancer.unsubscribe(subscriber_id)
        except Pyro4.errors.PyroError:
            pass
        
        return self.service.unsubscribe(subscriber_id)

    def get_subscribers(self):
        """
        Devuelve la lista de IDs de suscriptores

        Returns:
            list: Lista de IDs de suscriptores
        """
        # En esta versión, las suscripciones son gestionadas por el balanceador
        # Pero aún implementamos el method para mantener compatibilidad
        try:
            if self.balancer_uri:
                balancer = Pyro4.Proxy(self.balancer_uri)
                return balancer.get_subscribers()
        except Pyro4.errors.PyroError:
            pass
        
        return self.service.get_subscribers()
    
    def get_server_id(self):
        """
        Devuelve el identificador único de este servidor
        
        Returns:
            str: ID del servidor
        """
        return self.server_id

    def _broadcaster(self):
        """
        Method que se ejecuta en un hilo separado y envía insultos aleatorios
        a los suscriptores cada 5 segundos
        """
        while self.running:
            time.sleep(5)   # pausa de 5 segundos

            # Verificar si hay insultos
            insults = self.service.get_insults()
            if not insults:
                continue

            # Seleccionar un insulto aleatorio
            random_insult = random.choice(insults)
            
            # En el modo balanceado, enviar notificación al balanceador
            if self.balancer_uri:
                try:
                    balancer = Pyro4.Proxy(self.balancer_uri)
                    balancer.notify_subscribers(random_insult)
                    continue  # Si hay balanceador, no notificar localmente
                except Pyro4.errors.PyroError:
                    self.registered_with_balancer = False  # Marcar como no registrado si hay error
            
            # Si no hay balanceador o hubo error, notificar localmente
            if self.service.subscribers:
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
    
    def register_with_balancer(self, balancer_uri, this_uri):
        """
        Registra este servidor con el balanceador de carga
        
        Args:
            balancer_uri (str): URI del balanceador de carga
            this_uri (str): URI de este servidor
            
        Returns:
            bool: True si se registró correctamente
        """
        try:
            balancer = Pyro4.Proxy(balancer_uri)
            success = balancer.register_server(this_uri)
            if success:
                self.balancer_uri = balancer_uri
                self.registered_with_balancer = True
            return success
        except Pyro4.errors.PyroError as e:
            print(f"Error al registrarse con el balanceador: {e}")
            return False


def start_server(port=None, ns_host=None, ns_port=None, balancer_mode=False):
    """
    Inicia el servidor Pyro4 para el servicio de insultos
    
    Args:
        port (int, opcional): Puerto para el demonio Pyro4
        ns_host (str, opcional): Host del servidor de nombres Pyro4
        ns_port (int, opcional): Puerto del servidor de nombres Pyro4
        balancer_mode (bool): Si True, intentará registrarse con el balanceador
    """
    # Configurar la conexión al servidor de nombres si se especificó
    if ns_host or ns_port:
        ns_location = f"{ns_host or 'localhost'}:{ns_port or 9090}"
        os.environ["PYRO_NS_HOST"] = ns_host or "localhost"
        os.environ["PYRO_NS_PORT"] = str(ns_port or 9090)
    
    # Crear la instancia del servicio con un ID único
    server_id = f"insult_server_{socket.gethostname()}_{port or 'default'}"
    insult_service = PyroInsultService(server_id)
    
    # Crear opciones para el demonio
    daemon_args = {}
    if port:
        daemon_args["port"] = port
    
    # Registrar el servicio con el servidor de nombres
    daemon = Pyro4.Daemon(**daemon_args)
    
    try:
        ns = Pyro4.locateNS()
    except Pyro4.errors.PyroError as e:
        print(f"Error al conectar con el servidor de nombres: {e}")
        print("Asegúrate de que el servidor de nombres esté en ejecución")
        print("Puedes iniciarlo con: python -m Pyro4.naming")
        return
    
    # Generar un nombre único para este servidor
    service_name = f"insult.service.node.{server_id}"
    uri = daemon.register(insult_service)
    ns.register(service_name, uri)
    
    print(f"InsultService registrado como: {service_name}")
    print(f"URI: {uri}")
    
    # Si estamos en modo balanceador, intentar registrarse con él
    if balancer_mode:
        try:
            balancer_uri = ns.lookup("insult.service.balancer")
            if insult_service.register_with_balancer(str(balancer_uri), str(uri)):
                print("Registrado con éxito en el balanceador de carga")
            else:
                print("Error al registrarse con el balanceador")
        except Pyro4.errors.PyroError as e:
            print(f"No se pudo encontrar el balanceador: {e}")
            print("Ejecutando en modo independiente")
    
    print("Servidor iniciado...")
    daemon.requestLoop()    # bucle de eventos


if __name__ == "__main__":
    # Procesar argumentos de línea de comandos
    import argparse
    parser = argparse.ArgumentParser(description='Servidor InsultService')
    parser.add_argument('--port', type=int, help='Puerto para el demonio Pyro4')
    parser.add_argument('--ns-host', help='Host del servidor de nombres Pyro4')
    parser.add_argument('--ns-port', type=int, help='Puerto del servidor de nombres Pyro4')
    parser.add_argument('--balancer', action='store_true', help='Registrarse con el balanceador')
    
    args = parser.parse_args()
    
    start_server(args.port, args.ns_host, args.ns_port, args.balancer)
