import pika
import time
import threading
import uuid
import argparse
import statistics
import matplotlib.pyplot as plt

RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'filter_queue'

def send_messages(thread_id, num_messages, latencies):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    for i in range(num_messages):
        message = f"Message {i}: dummy tonoto test weon"
        correlation_id = str(uuid.uuid4())
        start_time = time.time()
        channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=f"FILTER:{message}",
            properties=pika.BasicProperties(
                reply_to='',
                correlation_id=correlation_id
            )
        )
        end_time = time.time()
        latency = end_time - start_time
        latencies.append(latency)

    connection.close()

def main():
    parser = argparse.ArgumentParser(description='Prueba de rendimiento para FilterService')
    parser.add_argument('--clients', type=int, default=1, help='Número de clientes concurrentes')
    parser.add_argument('--messages', type=int, default=10, help='Número de mensajes por cliente')
    args = parser.parse_args()

    total_messages = args.clients * args.messages
    latencies = []

    threads = []
    start_time = time.time()
    for i in range(args.clients):
        thread = threading.Thread(target=send_messages, args=(i, args.messages, latencies))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    end_time = time.time()

    duration = end_time - start_time
    throughput = total_messages / duration
    average_latency = statistics.mean(latencies)
    median_latency = statistics.median(latencies)
    p95_latency = statistics.quantiles(latencies, n=100)[94]

    print(f"\nResultados de la prueba:")
    print(f"Total de mensajes enviados: {total_messages}")
    print(f"Duración total: {duration:.2f} segundos")
    print(f"Throughput: {throughput:.2f} mensajes/segundo")
    print(f"Latencia promedio: {average_latency:.4f} segundos")
    print(f"Latencia mediana: {median_latency:.4f} segundos")
    print(f"Latencia percentil 95: {p95_latency:.4f} segundos")

    # Guardar resultados para análisis posterior
    with open("performance_results.csv", "a") as f:
        f.write(f"{args.clients},{args.messages},{total_messages},{duration:.4f},{throughput:.2f},{average_latency:.4f},{p95_latency:.4f}\n")

    # Histograma
    plt.figure(figsize=(10, 6))
    plt.hist(latencies, bins=50, color='skyblue', edgecolor='black')
    plt.title('Distribución de latencias')
    plt.xlabel('Latencia (segundos)')
    plt.ylabel('Frecuencia')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('latency_distribution.png')
    plt.show()

if __name__ == "__main__":
    main()
