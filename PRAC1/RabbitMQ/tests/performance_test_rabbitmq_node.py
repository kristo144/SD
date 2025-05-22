#!/usr/bin/env python3.13

"""
performance_test_rabbitmq_node.py

Prueba de rendimiento para un único nodo (instancia) de insult_service + insult_filter_service.
Ejecutar tras haber levantado ambos servicios y RabbitMQ.
"""
import os, sys
here = os.path.dirname(__file__)            # .../RabbitMQ/tests
root = os.path.abspath(os.path.join(here, '..'))
sys.path.insert(0, root)                    # ahora 'RabbitMQ' está en sys.path

import time
import threading
from clients.add_insult_client import add_insult
from clients.get_insults_client import get_insults
from clients.send_text_client import send_text
from clients.get_results_client import get_filtered_results

     # RPC para añadir insulto
    # RPC para recuperar lista
      # Publica en filter_queue
  # RPC filtrado

# CONFIGURACIÓN
N_REQUESTS = 1000        # nº total de peticiones
CONCURRENCY = 10       # nº de hilos simultáneos
SAMPLE_INSULT = "tonto" # insulto de prueba
SAMPLE_TEXT = "Esto es un insulto: tonto y bruto."  # texto para filtrar

latencies = []  # lista de tiempos (segundos)

def worker_add_and_get():
    """
    1) add_insult(SAMPLE_INSULT): RPC añade insulto
    2) get_insults(): RPC recupera la lista completa (incluye el recién añadido)
    """
    t0 = time.perf_counter()
    add_insult(SAMPLE_INSULT)
    _ = get_insults()
    t1 = time.perf_counter()
    latencies.append(t1 - t0)

def worker_filter_text():
    """
    1) send_text(SAMPLE_TEXT): publica en cola de filtrado
    2) get_filtered_results(): RPC recoge el texto filtrado
    """
    t0 = time.perf_counter()
    send_text(SAMPLE_TEXT)
    _ = get_filtered_results()
    t1 = time.perf_counter()
    latencies.append(t1 - t0)

def run_test(worker_fn, label):
    """
    Lanza N_REQUESTS tareas usando worker_fn en bloques de CONCURRENCY hilos.
    Al final imprime métricas básicas.
    """
    global latencies
    latencies = []
    threads = []

    print(f"\n--- Iniciando test [{label}] con {N_REQUESTS} peticiones y {CONCURRENCY} concurrencia ---")
    t_start = time.perf_counter()

    for i in range(N_REQUESTS):
        th = threading.Thread(target=worker_fn)
        th.start()
        threads.append(th)

        # Sincronizar cada CONCURRENCY hilos para controlar la ola
        if (i + 1) % CONCURRENCY == 0:
            for t in threads:
                t.join()
            threads = []

    # Esperar hilos restantes
    for t in threads:
        t.join()

    t_end = time.perf_counter()
    total_time = sum(latencies)
    avg_latency = total_time / len(latencies)
    throughput = """len(latencies""" N_REQUESTS/ (t_end - t_start)

    print(f"Tiempo total prueba: {t_end - t_start:.3f} s")
    print(f"Throughput ≈ {throughput:.2f} req/s")
    print(f"Latencia media ≈ {avg_latency*1000:.1f} ms")
    print(f"Latencia mínima/máxima: {min(latencies)*1000:.1f}/{max(latencies)*1000:.1f} ms")
    print("--- Fin test ---\n")

if __name__ == "__main__":
    # Test 1: añadir y recuperar insultos (RPC sobre insult_service)
    run_test(worker_add_and_get, "add+get_insults")

    # Test 2: envío y filtrado de texto (cola de trabajo + RPC)
    run_test(worker_filter_text, "filter_text")
