import Pyro4
import time
from multiprocessing import Process
import argparse
import os

# Función que simula un cliente enviando solicitudes add_insult
def client_task(num_requests):
    service = Pyro4.Proxy("PYRONAME:insult.service")
    pid = os.getpid()  # ID del proceso para generar insultos únicos
    start_time = time.time()
    for i in range(num_requests):
        try:
            service.add_insult(f"test insult {pid}_{i}")  # Insulto único por proceso
        except Exception as e:
            print(f"Error: {e}")
    end_time = time.time()
    duration = end_time - start_time
    print(f"Client {pid} completed {num_requests} requests in {duration:.2f} seconds")
    return duration

if __name__ == "__main__":
    # Configuración de argumentos para personalizar la prueba
    parser = argparse.ArgumentParser()
    parser.add_argument("--processes", type=int, default=5, help="Number of processes")
    parser.add_argument("--requests", type=int, default=1000, help="Number of requests per process")
    args = parser.parse_args()
    num_processes = args.processes
    num_requests_per_process = args.requests
    processes = []
    start_time = time.time()
    # Iniciar procesos concurrentes
    for _ in range(num_processes):
        p = Process(target=client_task, args=(num_requests_per_process,))
        p.start()
        processes.append(p)
    # Esperar a que terminen
    for p in processes:
        p.join()
    end_time = time.time()
    total_time = end_time - start_time
    total_requests = num_processes * num_requests_per_process
    throughput = total_requests / total_time
    # Mostrar resultados
    print(f"Total time: {total_time:.2f} seconds")
    print(f"Throughput: {throughput:.2f} requests per second")