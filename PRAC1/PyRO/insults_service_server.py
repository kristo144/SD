import Pyro4
from insults_service import InsultService

if __name__ == '__main__':
    # Creamos un daemon y nos conectamos al Name Server
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    # Registramos la clase InsultService y obtenemos su URI
    uri = daemon.register(InsultService)
    # Asociamos un nombre al objeto en el Name Server
    ns.register("example.insult.service", uri)
    print(f"InsultService disponible en: {uri}")
    # Entramos en el bucle de procesamiento de peticiones
    daemon.requestLoop()