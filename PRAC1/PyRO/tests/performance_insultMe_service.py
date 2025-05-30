import argparse
import time
import multiprocessing
import itertools
import Pyro4
import Pyro4.errors
import sys

def discover_active_uris(base_name="insult.service", max_nodes=3):
    """Descubre URIs activas de insult.service.{A,B,C} en el NameServer."""
    ns = Pyro4.locateNS()
    uris = []
    for suffix in list("ABC")[:max_nodes]:
        name = f"{base_name}.{suffix}"
        try:
            uri = ns.lookup(name)
            proxy = Pyro4.Proxy(uri)
            proxy._pyroBind()
            #proxy.ping()  # chequeo de vida
            uris.append(uri)
            print(f"[+] Nodo activo: {name} -> {uri}")
        except (Pyro4.errors.NamingError, Pyro4.errors.CommunicationError):
            print(f"[-] Nodo {name} no responde, se ignora.")
    if not uris:
        print("ERROR: no se detectó ningún nodo activo. Salvo.")
        sys.exit(1)
    return uris

def worker(uri_list, requests_per_proc):
    """
    Función que corre en cada proceso:
    - Reconstruye proxies Pyro4.
    - Hace `requests_per_proc` llamadas insult_me en round-robin.
    """
    proxies = [Pyro4.Proxy(uri) for uri in uri_list]
    rr = itertools.cycle(proxies)
    done = 0
    for _ in range(requests_per_proc):
        proxy = next(rr)
        try:
            _ = proxy.insult_me()
        except Pyro4.errors.CommunicationError:
            # si falla un proxy, saltar esta petición
            continue
        done += 1
    return done

def main():
    parser = argparse.ArgumentParser(
        description="Stress test para insult_service.insult_me()"
    )
    parser.add_argument(
        "-p", "--processes", type=int, default=multiprocessing.cpu_count(),
        help="Número de procesos (default: cores CPU)"
    )
    parser.add_argument(
        "-r", "--requests", type=int, default=10000,
        help="Requests por proceso (default: 10000)"
    )
    args = parser.parse_args()

    # Descubrir nodos activos
    uris = discover_active_uris()

    total_procs = args.processes
    req_per = args.requests
    total_requests = total_procs * req_per
    print(f"\n[Test] Lanzando {total_procs} procesos × {req_per} peticiones = {total_requests} reqs\n")

    # Lanzar pool de procesos
    start = time.time()
    with multiprocessing.Pool(processes=total_procs) as pool:
        results = pool.starmap(worker, [(uris, req_per)] * total_procs)
    end = time.time()

    # Recoger resultados
    succeeded = sum(results)
    duration = end - start
    throughput = succeeded / duration if duration > 0 else 0

    print("===== Resultados =====")
    print(f"Total intentos   : {total_requests}")
    print(f"Total éxitos     : {succeeded}")
    print(f"Tiempo total     : {duration:.3f} s")
    print(f"Throughput       : {throughput:.1f} req/s")

if __name__ == "__main__":
    main()
