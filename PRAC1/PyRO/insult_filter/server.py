import Pyro4
import Pyro4.errors
from PRAC1.PyRO.insult_filter.model import InsultFilter

"""
    Implementación del servicio de filtrado de insultos usando Pyro4.
    Permite filtrar textos consultando la lista de insultos del InsultService.
"""

@Pyro4.expose
class PyroInsultFilter:
    def __init__(self):
        self.filter = InsultFilter()

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


def start_server():
    """
    Inicia el servidor Pyro4 para el servicio de filtrado
    """
    filter_service = PyroInsultFilter() # Crear la instancia del servicio

    # Registrar el servicio con el servidor de nombres
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(filter_service)
    ns.register("filter.service", uri)

    print("InsultFilter registrado como: filter.service")
    print(f"URI: {uri}")
    print("Servidor iniciado...")

    daemon.requestLoop()    # bucle de eventos


if __name__ == "__main__":
    start_server()