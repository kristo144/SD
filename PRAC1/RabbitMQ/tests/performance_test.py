#!/usr/bin/env python3

import pika
import uuid
import time
import csv
import random
import string

# Cliente RPC para probar el servicio de filtrado de insultos.
class InsultFilterRpcClient:
    def __init__(self, rabbitmq_host='localhost'):
        # Conexión al broker RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        self.channel = self.connection.channel()
        # Cola exclusiva para recibir respuestas RPC
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        # Consumir respuestas RPC
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True
        )
        # Almacenar respuestas y tiempos de llegada
        self.responses = {}

    def on_response(self, ch, method, props, body):
        # Callback al recibir respuesta del servicio de filtrado
        # Guardar respuesta junto con su identificador de correlación y tiempo de llegada
        self.responses[props.correlation_id] = (body.decode(), time.time())

def generar_texto_aleatorio(longitud):
    # Generar texto aleatorio de cierta longitud (solo letras y espacios)
    caracteres = string.ascii_letters + ' '
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def main():
    # Configuración inicial
    NUM_MENSAJES = 100  # Número de mensajes a enviar (ajustable)
    cliente_rpc = InsultFilterRpcClient()

    tiempos_envio = {}
    print(f"Enviando {NUM_MENSAJES} mensajes de prueba al servicio de filtrado...")

    # Registrar el tiempo de envío del primer mensaje
    tiempo_inicio_total = time.time()

    # Enviar todos los mensajes con texto aleatorio
    for i in range(NUM_MENSAJES):
        texto = generar_texto_aleatorio(50)
        corr_id = str(uuid.uuid4())
        tiempos_envio[corr_id] = time.time()
        cliente_rpc.channel.basic_publish(
            exchange='',
            routing_key='filter_rpc_queue',
            properties=pika.BasicProperties(
                reply_to=cliente_rpc.callback_queue,
                correlation_id=corr_id
            ),
            body=texto.encode()
        )

    # Esperar las respuestas de todos los mensajes
    while len(cliente_rpc.responses) < NUM_MENSAJES:
        cliente_rpc.connection.process_data_events(time_limit=0.1)

    # Registrar el tiempo final
    tiempo_fin_total = time.time()

    # Cálculos de rendimiento
    tiempo_total = tiempo_fin_total - tiempo_inicio_total
    throughput = NUM_MENSAJES / tiempo_total if tiempo_total > 0 else 0

    # Calcular latencia media por mensaje
    latencias = []
    for corr_id, (response_text, tiempo_llegada) in cliente_rpc.responses.items():
        if corr_id in tiempos_envio:
            latencias.append(tiempo_llegada - tiempos_envio[corr_id])
    latencia_media = sum(latencias) / len(latencias) if latencias else 0

    # Guardar resultados en CSV
    with open('resultados.csv', mode='w', newline='') as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(['num_mensajes', 'tiempo_total_s', 'throughput_msg_s', 'latencia_media_s'])
        escritor.writerow([NUM_MENSAJES, f"{tiempo_total:.4f}", f"{throughput:.2f}", f"{latencia_media:.4f}"])

    print("Prueba completada.")
    print(f"Tiempo total: {tiempo_total:.4f} s, Throughput: {throughput:.2f} mensajes/s, Latencia media: {latencia_media:.4f} s")

    cliente_rpc.connection.close()

if __name__ == '__main__':
    main()
