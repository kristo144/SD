import Pyro4
from Pyro4 import Proxy, Daemon
import threading
import time

# Clase callback para recibir insultos
@Pyro4.expose
class ClientCallback(object):
    def notify(self, insult):
        print(f"[Broadcast] Nuevo insulto: {insult}")

def main():
    # 1. Creamos el Daemon del cliente
    with Daemon() as client_daemon:
        # 2. Registramos el callback y obtenemos el URI
        callback = ClientCallback()
        callback_uri = client_daemon.register(callback)
        print(f"Callback disponible en: {callback_uri}")

        # 3. Conectamos al servicio remoto usando el Name Server
        service = Proxy("PYRONAME:example.insult.service")

        # 4. Enviamos al servidor el callback URI
        service.subscribe(callback_uri)

        # 5. Arrancamos el Daemon en un hilo aparte para no bloquear el main thread
        def loop_daemon():
            print("Entrando en bucle de escucha para callbacks...")
            client_daemon.requestLoop()

        daemon_thread = threading.Thread(target=loop_daemon, daemon=True)
        daemon_thread.start()

        # 6. Dejamos el main thread en un bucle infinito para mantener vivo el cliente
        try:
            while True:
                time.sleep(1)  # Evitamos consumo alto de CPU
        except KeyboardInterrupt:
            print("\nCliente detenido por usuario.")

if __name__ == "__main__":
    main()
