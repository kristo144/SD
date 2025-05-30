import os
import sys
import threading
import time
import random
import argparse

import Pyro4
from model import InsultService

@Pyro4.expose
class PyroInsultService:
    def __init__(self, insults_file):
        self.service = InsultService()
        # Precargar insultos desde fichero .txt
        if os.path.isfile(insults_file):
            with open(insults_file, encoding='utf-8') as f:
                for line in f:
                    insult = line.strip()
                    if insult:
                        self.service.add_insult(insult)
        # Arrancar broadcaster en hilo demonio
        self.running = True
        t = threading.Thread(target=self._broadcaster)
        t.daemon = True
        t.start()

    def add_insult(self, insult):
        return self.service.add_insult(insult)

    def get_insults(self):
        return self.service.get_insults()

    def subscribe(self, subscriber_id, callback):
        return self.service.subscribe(subscriber_id, callback)

    def unsubscribe(self, subscriber_id):
        return self.service.unsubscribe(subscriber_id)

    def get_subscribers(self):
        return self.service.get_subscribers()

    def insult_me(self):
        """
        Devuelve un único insulto aleatorio al momento.
        """
        insults = self.service.get_insults()
        if insults:
            return random.choice(insults)
        else:
            return None

    def _broadcaster(self):
        while self.running:
            time.sleep(5)
            insults = self.service.get_insults()
            if not insults or not self.service.subscribers:
                continue
            insult = random.choice(insults)
            to_remove = []
            for sid, cb in self.service.subscribers.items():
                try:
                    cb.notify(insult)
                except:
                    to_remove.append(sid)
            for sid in to_remove:
                self.service.unsubscribe(sid)

def main():
    parser = argparse.ArgumentParser(description="PyRO4 InsultService estático.")
    parser.add_argument(
        "--name", "-n", default="A",
        help="Sufijo de registro en el NameServer (A, B, C...)"
    )
    parser.add_argument(
        "--insults-file", "-f", default="insults.txt",
        help="Ruta al fichero de insultos precargados"
    )
    args = parser.parse_args()

    # Arrancar Pyro daemon y registrar servicio
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    service = PyroInsultService(args.insults_file)
    uri = daemon.register(service)
    regname = f"insult.service.{args.name}"
    ns.register(regname, uri)

    print(f"[*] InsultService registrado como: {regname}")
    print(f"    URI: {uri}")
    print("[*] Esperando peticiones...")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
