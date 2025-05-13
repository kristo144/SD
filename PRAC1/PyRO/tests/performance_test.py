import sys
import os
import time
import random
import string
import threading
import multiprocessing
import Pyro4
from concurrent.futures import ThreadPoolExecutor

# Añadir el directorio raíz al path para importaciones relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def generate_random_text(length=100):
    """Genera un texto aleatorio de la longitud especificada"""
    return ''.join(random.choice(string.ascii_letters + ' ') for _ in range(length))


def generate_random_insult(length=8):
    """Genera un insulto aleatorio de la longitud especificada"""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))


def test_insult_service_performance(num_requests=1000, parallel=10):
    """
    Prueba de rendimiento para InsultService

    Args:
        num_requests: Número total de solicitudes a realizar
        parallel: Número de hilos paralelos

    Returns:
        float: Tiempo promedio por solicitud en segundos
    """
    try:
        # Conectar con el servicio
        insult_service = Pyro4.Proxy("PYRONAME:insult.service")

        # Generar insultos aleatorios
        insults = [generate_random_insult() for _ in range(100)]

        # Función para realizar solicitudes
        def make_request():
            operation = random.choice(['add', 'get'])
            if operation == 'add':
                insult = random.choice(insults)
                insult_service.add_insult(insult)
            else:
                insult_service.get_insults()

        # Cronometrar las solicitudes
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            for future in futures:
                future.result()

        end_time = time.time()
        total_time = end_time - start_time

        # Calcular métricas
        requests_per_second = num_requests / total_time
        avg_time_per_request = total_time / num_requests

        print(f"== Test InsultService Performance ==")
        print(f"Número de solicitudes: {num_requests}")
        print(f"Hilos paralelos: {parallel}")
        print(f"Tiempo total: {total_time:.2f} segundos")
        print(f"Solicitudes por segundo: {requests_per_second:.2f}")
        print(f"Tiempo promedio por solicitud: {avg_time_per_request * 1000:.2f} ms")

        return avg_time_per_request

    except Pyro4.errors.PyroError as e:
        print(f"Error de Pyro4: {e}")
        return None


def test_insult_filter_performance(num_requests=1000, parallel=10):
    """
    Prueba de rendimiento para InsultFilter

    Args:
        num_requests: Número total de solicitudes a realizar
        parallel: Número de hilos paralelos

    Returns:
        float: Tiempo promedio por solicitud en segundos
    """
    try:
        # Conectar con el servicio
        filter_service = Pyro4.Proxy("PYRONAME:filter.service")

        # Generar textos aleatorios
        texts = [generate_random_text() for _ in range(100)]

        # Función para realizar solicitudes
        def make_request():
            operation = random.choice(['filter', 'get'])
            if operation == 'filter':
                text = random.choice(texts)
                filter_service.filter_text(text)
            else:
                filter_service.get_filtered_texts()

        # Cronometrar las solicitudes
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=parallel) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            for future in futures:
                future.result()

        end_time = time.time()
        total_time = end_time - start_time

        # Calcular métricas
        requests_per_second = num_requests / total_time
        avg_time_per_request = total_time / num_requests

        print(f"== Test InsultFilter Performance ==")
        print(f"Número de solicitudes: {num_requests}")
        print(f"Hilos paralelos: {parallel}")
        print(f"Tiempo total: {total_time:.2f} segundos")
        print(f"Solicitudes por segundo: {requests_per_second:.2f}")
        print(f"Tiempo promedio por solicitud: {avg_time_per_request * 1000:.2f} ms")

        return avg_time_per_request

    except Pyro4.errors.PyroError as e:
        print(f"Error de Pyro4: {e}")
        return None


def test_scaling(service_type, num_requests=1000, workers_range=[1, 2, 3]):
    """
    Prueba el escalado estático para un tipo de servicio

    Args:
        service_type: 'insult' o 'filter'
        num_requests: Número total de solicitudes
        workers_range: Lista con el número de trabajadores a probar

    Returns:
        dict: Diccionario con los tiempos para cada configuración
    """
    results = {}

    for workers in workers_range:
        print(f"\nPrueba con {workers} {'trabajador' if workers == 1 else 'trabajadores'}:")

        if service_type == 'insult':
            avg_time = test_insult_service_performance(num_requests, workers)
        else:
            avg_time = test_insult_filter_performance(num_requests, workers)

        if avg_time is not None:
            results[workers] = avg_time

    # Calcular speedup relativo al caso con un trabajador
    if 1 in results and results[1] > 0:
        base_time = results[1]
        speedups = {w: base_time / t for w, t in results.items()}

        print("\n== Resultados de Speedup ==")
        for workers, speedup in speedups.items():
            print(f"Speedup con {workers} {'trabajador' if workers == 1 else 'trabajadores'}: {speedup:.2f}x")

    return results


def main():
    """Función principal para ejecutar las pruebas"""
    print("=== Iniciando pruebas de rendimiento ===\n")

    # Número de solicitudes para las pruebas
    num_requests = 1000

    # Rangos de trabajadores para probar
    workers_range = [1, 2, 3, 4]

    # Probar InsultService
    print("\n***** PRUEBAS PARA INSULT SERVICE *****")
    insult_results = test_scaling('insult', num_requests, workers_range)

    # Probar InsultFilter
    print("\n***** PRUEBAS PARA INSULT FILTER *****")
    filter_results = test_scaling('filter', num_requests, workers_range)

    print("\n=== Pruebas de rendimiento completadas ===")


if __name__ == "__main__":
    main()