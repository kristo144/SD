import Pyro4
import Pyro4.errors
import sys
import os
import socket

# Añadir el directorio raíz al path para importaciones relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar el modelo original
from model import InsultFilter

"""
    Implementación modificada del servicio de filtrado usando Pyro4 para su exposición remota.
    Esta versión está diseñada para trabajar con el sistema de balanceo de carga.
"""

@Pyro4.expose
class PyroInsultFilter:
    def __init__(self, server_id=None):
        self.filter = InsultFilter()
        self.server_id = server_id or socket.gethostname()
        
        # Para sincronización con el balanceador de carga
        self.registered_with_balancer = False
        self.balancer_uri = None

    def filter_text(self, text):
        """
        Filtra un texto reemplazando los insultos por "CENSORED"

        Args:
            text (str): El texto a filtrar

        Returns:
            str: El texto con los insultos censurados
        """
        try:
            # Conectar con el servicio de insultos para obtener la lista actual
            insult_service = Pyro4.Proxy("PYRONAME:insult.service")
            insults = insult_service.get_insults()

            # Aplicar el filtro
            return self.filter.filter_text(text, insults)
        except Pyro4.errors.PyroError as e:
            print(f"Error al conectar con InsultService: {e}")
            # Si hay error, devolver el texto sin filtrar y no almacenarlo
            return text

    def get_filtered_texts(self):
        """
        Devuelve la lista de textos filtrados

        Returns:
            list: Lista de textos filtrados
        """
        return self.filter.get_filtered_texts()
    
    def get_server_id(self):
        """
        Devuelve el identificador único de este servidor
        
        Returns:
            str: ID del servidor
        """
        return self.server_id
    
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
    Inicia el servidor Pyro4 para el servicio de filtrado
    
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
    server_id = f"filter_server_{socket.gethostname()}_{port or 'default'}"
    filter_service = PyroInsultFilter(server_id)
    
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
    service_name = f"filter.service.node.{server_id}"
    uri = daemon.register(filter_service)
    ns.register(service_name, uri)
    
    print(f"InsultFilter registrado como: {service_name}")
    print(f"URI: {uri}")
    
    # Si estamos en modo balanceador, intentar registrarse con él
    if balancer_mode:
        try:
            balancer_uri = ns.lookup("filter.service.balancer")
            if filter_service.register_with_balancer(str(balancer_uri), str(uri)):
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
    parser = argparse.ArgumentParser(description='Servidor InsultFilter')
    parser.add_argument('--port', type=int, help='Puerto para el demonio Pyro4')
    parser.add_argument('--ns-host', help='Host del servidor de nombres Pyro4')
    parser.add_argument('--ns-port', type=int, help='Puerto del servidor de nombres Pyro4')
    parser.add_argument('--balancer', action='store_true', help='Registrarse con el balanceador')
    
    args = parser.parse_args()
    
    start_server(args.port, args.ns_host, args.ns_port, args.balancer)
