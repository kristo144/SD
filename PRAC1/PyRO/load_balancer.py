import Pyro4
import Pyro4.errors
import random
import threading
import time
import socket
import sys

class LoadBalancer:
    """
    Balanceador de carga para servicios Pyro4.
    Implementa una estrategia de Round-Robin y verificación de disponibilidad.
    """
    
    def __init__(self, service_name):
        """
        Inicializa el balanceador de carga para un tipo de servicio específico
        
        Args:
            service_name (str): Nombre del servicio ('insult' o 'filter')
        """
        self.service_name = service_name
        self.servers = []  # Lista de URIs de servidores disponibles
        self.current_server = 0  # Índice para round-robin
        self.lock = threading.Lock()  # Para sincronización de acceso a la lista de servidores
        self.running = True
        
        # Iniciar el hilo de verificación de disponibilidad
        self.health_check_thread = threading.Thread(target=self._health_check)
        self.health_check_thread.daemon = True
        self.health_check_thread.start()
    
    def register_server(self, server_uri):
        """
        Registra un nuevo servidor en el balanceador
        
        Args:
            server_uri (str): URI del servidor Pyro4
            
        Returns:
            bool: True si se registró correctamente
        """
        with self.lock:
            if server_uri not in self.servers:
                self.servers.append(server_uri)
                print(f"Servidor registrado: {server_uri}")
                return True
            return False
    
    def unregister_server(self, server_uri):
        """
        Elimina un servidor del balanceador
        
        Args:
            server_uri (str): URI del servidor Pyro4
            
        Returns:
            bool: True si se eliminó correctamente
        """
        with self.lock:
            if server_uri in self.servers:
                self.servers.remove(server_uri)
                print(f"Servidor eliminado: {server_uri}")
                return True
            return False
    
    def get_server(self):
        """
        Obtiene el siguiente servidor usando round-robin
        
        Returns:
            str: URI del servidor, o None si no hay servidores disponibles
        """
        with self.lock:
            if not self.servers:
                return None
            
            # Implementación de Round-Robin
            server = self.servers[self.current_server]
            self.current_server = (self.current_server + 1) % len(self.servers)
            
            return server
    
    def get_all_servers(self):
        """
        Devuelve la lista completa de servidores registrados
        
        Returns:
            list: Lista de URIs de servidores
        """
        with self.lock:
            return self.servers.copy()
    
    def _health_check(self):
        """
        Verifica periódicamente la disponibilidad de los servidores
        """
        while self.running:
            time.sleep(5)  # Verificar cada 5 segundos
            
            with self.lock:
                servers_to_check = self.servers.copy()
            
            for server_uri in servers_to_check:
                try:
                    # Intentar hacer ping al servidor
                    proxy = Pyro4.Proxy(server_uri)
                    proxy._pyroBind()
                    # Si hay timeout o error, se eliminará en except
                except (Pyro4.errors.PyroError, socket.error):
                    print(f"Servidor no disponible: {server_uri}")
                    self.unregister_server(server_uri)
    
    def shutdown(self):
        """
        Detiene el balanceador de carga
        """
        self.running = False
        if self.health_check_thread.is_alive():
            self.health_check_thread.join(1)  # Esperar max 1 segundo


@Pyro4.expose
class InsultServiceLoadBalancer:
    """
    Balanceador de carga para InsultService.
    Implementa la misma interfaz que InsultService para ser transparente para los clientes.
    """
    
    def __init__(self):
        self.balancer = LoadBalancer('insult')
        self.subscribers = {}  # Diccionario para mantener suscriptores (clave: id, valor: callback)
    
    def add_insult(self, insult):
        """
        Añade un insulto a todos los servidores registrados
        
        Args:
            insult (str): El insulto a añadir
            
        Returns:
            bool: True si se añadió con éxito en al menos un servidor
        """
        success = False
        server_uri = self.balancer.get_server()
        
        if not server_uri:
            print("No hay servidores disponibles")
            return False
        
        try:
            # Intentar añadir el insulto en el servidor seleccionado
            proxy = Pyro4.Proxy(server_uri)
            success = proxy.add_insult(insult)
            
            # Si se añadió con éxito, propagar a todos los demás servidores
            if success:
                for other_uri in self.balancer.get_all_servers():
                    if other_uri != server_uri:
                        try:
                            other_proxy = Pyro4.Proxy(other_uri)
                            other_proxy.add_insult(insult)
                        except Pyro4.errors.PyroError:
                            pass  # Ignorar errores en la propagación
        
        except Pyro4.errors.PyroError as e:
            print(f"Error al añadir insulto: {e}")
            self.balancer.unregister_server(server_uri)
        
        return success
    
    def get_insults(self):
        """
        Obtiene la lista de insultos de un servidor aleatorio
        
        Returns:
            list: Lista de insultos almacenados
        """
        server_uri = self.balancer.get_server()
        
        if not server_uri:
            print("No hay servidores disponibles")
            return []
        
        try:
            proxy = Pyro4.Proxy(server_uri)
            return proxy.get_insults()
        
        except Pyro4.errors.PyroError as e:
            print(f"Error al obtener insultos: {e}")
            self.balancer.unregister_server(server_uri)
            return []
    
    def subscribe(self, subscriber_id, callback):
        """
        Registra un suscriptor para recibir insultos aleatorios
        
        Args:
            subscriber_id (str): Identificador único del suscriptor
            callback: Objeto callback para notificar al suscriptor
            
        Returns:
            bool: True si la suscripción fue exitosa
        """
        # Guardamos el callback localmente
        self.subscribers[subscriber_id] = callback
        return True
    
    def unsubscribe(self, subscriber_id):
        """
        Elimina un suscriptor de la lista de suscriptores
        
        Args:
            subscriber_id (str): Identificador único del suscriptor
            
        Returns:
            bool: True si se eliminó, False si no existía
        """
        if subscriber_id in self.subscribers:
            del self.subscribers[subscriber_id]
            return True
        return False
    
    def get_subscribers(self):
        """
        Devuelve la lista de IDs de suscriptores
        
        Returns:
            list: Lista de IDs de suscriptores
        """
        return list(self.subscribers.keys())
    
    def register_server(self, server_uri):
        """
        Registra un nuevo servidor en el balanceador
        
        Args:
            server_uri (str): URI del servidor
            
        Returns:
            bool: True si se registró correctamente
        """
        return self.balancer.register_server(server_uri)
    
    def unregister_server(self, server_uri):
        """
        Elimina un servidor del balanceador
        
        Args:
            server_uri (str): URI del servidor
            
        Returns:
            bool: True si se eliminó correctamente
        """
        return self.balancer.unregister_server(server_uri)
    
    def get_registered_servers(self):
        """
        Devuelve la lista de servidores registrados
        
        Returns:
            list: Lista de URIs de servidores
        """
        return self.balancer.get_all_servers()
    
    def notify_subscribers(self, insult):
        """
        Notifica a todos los suscriptores con un insulto
        Este method es llamado por los servidores
        
        Args:
            insult (str): Insulto a notificar
        """
        subscribers_to_remove = []
        
        for subscriber_id, callback in self.subscribers.items():
            try:
                callback.notify(insult)
            except Exception:
                # Si hay error al notificar, eliminar el suscriptor
                subscribers_to_remove.append(subscriber_id)
        
        # Eliminar suscriptores con error
        for subscriber_id in subscribers_to_remove:
            self.unsubscribe(subscriber_id)


@Pyro4.expose
class InsultFilterLoadBalancer:
    """
    Balanceador de carga para InsultFilter.
    Implementa la misma interfaz que InsultFilter para ser transparente para los clientes.
    """
    
    def __init__(self):
        self.balancer = LoadBalancer('filter')
        self.filtered_texts = []  # Lista centralizada de textos filtrados
    
    def filter_text(self, text):
        """
        Filtra un texto reemplazando los insultos por "CENSORED"
        
        Args:
            text (str): El texto a filtrar
            
        Returns:
            str: El texto con los insultos censurados
        """
        server_uri = self.balancer.get_server()
        
        if not server_uri:
            print("No hay servidores disponibles")
            return text
        
        try:
            proxy = Pyro4.Proxy(server_uri)
            filtered_text = proxy.filter_text(text)
            
            # Almacenar el resultado en la lista centralizada
            self.filtered_texts.append(filtered_text)
            
            return filtered_text
        
        except Pyro4.errors.PyroError as e:
            print(f"Error al filtrar texto: {e}")
            self.balancer.unregister_server(server_uri)
            return text
    
    def get_filtered_texts(self):
        """
        Devuelve la lista centralizada de textos filtrados
        
        Returns:
            list: Lista de textos filtrados
        """
        return self.filtered_texts
    
    def register_server(self, server_uri):
        """
        Registra un nuevo servidor en el balanceador
        
        Args:
            server_uri (str): URI del servidor
            
        Returns:
            bool: True si se registró correctamente
        """
        return self.balancer.register_server(server_uri)
    
    def unregister_server(self, server_uri):
        """
        Elimina un servidor del balanceador
        
        Args:
            server_uri (str): URI del servidor
            
        Returns:
            bool: True si se eliminó correctamente
        """
        return self.balancer.unregister_server(server_uri)
    
    def get_registered_servers(self):
        """
        Devuelve la lista de servidores registrados
        
        Returns:
            list: Lista de URIs de servidores
        """
        return self.balancer.get_all_servers()


def start_insult_service_load_balancer():
    """
    Inicia el balanceador de carga para InsultService
    """
    lb = InsultServiceLoadBalancer()
    
    # Registrar el balanceador con el servidor de nombres
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(lb)
    
    # Registrar como el servicio principal
    ns.register("insult.service.balancer", uri)
    # También registrar como el servicio normal para ser transparente a los clientes existentes
    ns.register("insult.service", uri)
    
    print("InsultService LoadBalancer registrado como: insult.service.balancer y insult.service")
    print(f"URI: {uri}")
    print("Balanceador iniciado...")
    
    daemon.requestLoop()


def start_insult_filter_load_balancer():
    """
    Inicia el balanceador de carga para InsultFilter
    """
    lb = InsultFilterLoadBalancer()
    
    # Registrar el balanceador con el servidor de nombres
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(lb)
    
    # Registrar como el servicio principal
    ns.register("filter.service.balancer", uri)
    # También registrar como el servicio normal para ser transparente a los clientes existentes
    ns.register("filter.service", uri)
    
    print("InsultFilter LoadBalancer registrado como: filter.service.balancer y filter.service")
    print(f"URI: {uri}")
    print("Balanceador iniciado...")
    
    daemon.requestLoop()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python load_balancer.py [insult|filter]")
        sys.exit(1)
    
    service_type = sys.argv[1].lower()
    
    if service_type == "insult":
        start_insult_service_load_balancer()
    elif service_type == "filter":
        start_insult_filter_load_balancer()
    else:
        print("Servicio no válido. Use 'insult' o 'filter'")
        sys.exit(1)
