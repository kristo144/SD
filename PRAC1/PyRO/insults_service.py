import threading
import time
import random
import Pyro4

# clase para PyRO
@Pyro4.expose
class InsultService:
    def __init__(self):
        # Lista de insultos almacenados
        self.insults = []
        # Lista de callbacks registrados (proxies de cliente)
        self.subscribers = []
        # Iniciamos hilo demonio para emisiones periódicas
        self._broadcast_thread = threading.Thread(
            target=self._broadcaster_loop,
            daemon=True
        )
        self._broadcast_thread.start()

    def add_insult(self, insult: str) -> bool:
        """Añade un insulto a la lista si no está vacío."""
        if insult:
            self.insults.append(insult)
            return True
        return False

    def get_insults(self) -> list[str]:  # type: ignore[type-arg]
        """Devuelve la lista actual de insultos."""
        return list(self.insults)

    def subscribe(self, callback) -> bool:
        """Registra un proxy de callback para recibir emisiones."""
        try:
            self.subscribers.append(callback)
            return True
        except Exception as e:
            print(f"Error al suscribir cliente: {e}")
            return False

    def _broadcaster_loop(self):
        """Bucle interno: cada 5s envía un insulto aleatorio a los suscriptores."""
        while True:
            time.sleep(5)
            if not self.insults or not self.subscribers:
                continue
            insult = random.choice(self.insults)
            # Notificamos a cada subscriber
            for callback in list(self.subscribers):
                try:
                    callback.notify(insult)
                except Exception:
                    # Eliminamos suscriptores muertos
                    self.subscribers.remove(callback)