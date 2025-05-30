import Pyro4
import Pyro4.errors
import threading
import uuid
import itertools
import sys

@Pyro4.expose
class InsultCallback:
    """Callback para recibir insultos aleatorios."""
    def notify(self, insult):
        print(f"\n[RANDOM INSULT]: {insult}")
        return True

def discover_services(ns, base_name="insult.service", max_nodes=3):
    """Consulta al NameServer y devuelve lista de proxies disponibles."""
    proxies = []
    for suffix in list("ABC")[:max_nodes]:
        fullname = f"{base_name}.{suffix}"
        try:
            uri = ns.lookup(fullname)
            proxies.append((fullname, Pyro4.Proxy(uri)))
            print(f"[+] Nodo encontrado: {fullname} -> {uri}")
        except Pyro4.errors.NamingError:
            # no registrado, lo ignoramos
            pass
    if not proxies:
        print("[-] No se encontraron nodos de insult.service.*. Saliendo...")
        sys.exit(1)
    return proxies

def main():
    # Conectarse al NameServer
    ns = Pyro4.locateNS()
    # Descubrir hasta 3 nodos (A, B, C)
    nodes = discover_services(ns)
    # Iterator para round-robin
    rr = itertools.cycle(nodes)

    # Preparar callback y daemon para recibir notificaciones
    callback = InsultCallback()
    daemon = Pyro4.Daemon()
    cb_uri = daemon.register(callback)
    client_id = str(uuid.uuid4())

    # Thread de Pyro para callbacks
    t = threading.Thread(target=daemon.requestLoop)
    t.daemon = True
    t.start()

    subscribed = False

    while True:
        print("\n=== Cliente InsultService ===")
        print("1) Añadir insulto")
        print("2) Ver insultos")
        print("3) InsultMe")
        print("4) Suscribirse a todos")
        print("5) Cancelar suscripción a todos")
        print("6) Salir...")
        opt = input("Elige (1-6): ").strip()

        if opt == "1":
            _, proxy = next(rr)
            insult = input("Insulto a añadir: ").strip()
            ok = proxy.add_insult(insult)
            print("OK" if ok else "Ya existe o no valid")

        elif opt == "2":
            _, proxy = next(rr)
            lst = proxy.get_insults()
            print("\n-- Insult List --")
            for i, ins in enumerate(lst, 1):
                print(f"{i}. {ins}")

        elif opt == "3":
            _, proxy = next(rr)
            try:
                insult = proxy.insult_me()
                if insult:
                    print(f"\n{insult}")
                else:
                    print(f"\nEmpty InsultList")
            except Pyro4.errors.PyroError as e:
                print(f"Error al solicitar insult_me: {e}")

        elif opt == "4":
            if not subscribed:
                for name, proxy in nodes:
                    sid = f"{client_id}.{name}"
                    proxy.subscribe(sid, callback)
                subscribed = True
                print("[+] Suscrito a todos los nodos.")
            else:
                print("Already subscribed.")

        elif opt == "5":
            if subscribed:
                for name, proxy in nodes:
                    sid = f"{client_id}.{name}"
                    proxy.unsubscribe(sid)
                subscribed = False
                print("[+] Suscripción cancelada en todos.")
            else:
                print("Not suscribed yet.")

        elif opt == "6":
            if subscribed:
                for name, proxy in nodes:
                    sid = f"{client_id}.{name}"
                    proxy.unsubscribe(sid)
            print("\t**SALIENDO**")
            break

        else:
            print("No valid option.")

if __name__ == "__main__":
    main()
