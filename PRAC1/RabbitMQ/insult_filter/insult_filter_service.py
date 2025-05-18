#!/usr/bin/env python3.13

import pika
import uuid
import json

# Servicio que filtra insultos en textos usando RPC para obtener la lista de insultos actual.
class InsultFilterService:
    def __init__(self, rabbitmq_host='localhost'):
        # Conexión principal para recibir peticiones de filtrado
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        self.channel = self.connection.channel()

        # Declarar la cola RPC para el servicio de filtrado
        self.channel.queue_declare(queue='filter_rpc_queue')

        # Configurar calidad de servicio para procesar de a un mensaje por vez
        self.channel.basic_qos(prefetch_count=1)
        # Iniciar consumo con la función de callback para procesar peticiones
        self.channel.basic_consume(queue='filter_rpc_queue', on_message_callback=self.on_request)

        # Conexión secundaria para consultar el servicio InsultService (RPC)
        self.insult_connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        self.insult_channel = self.insult_connection.channel()
        # Cola de respuesta exclusiva para recibir la lista de insultos
        result = self.insult_channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        self.insult_channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_insult_response,
            auto_ack=True
        )
        # Variables para la respuesta del servicio InsultService
        self.insult_response = None
        self.insult_corr_id = None

    def on_insult_response(self, ch, method, props, body):
        # Callback para recibir la lista de insultos desde InsultService
        if self.insult_corr_id == props.correlation_id:
            # Decodificar la lista de insultos (se espera JSON)
            try:
                insults = json.loads(body.decode())
            except Exception:
                insults = []
            self.insult_response = insults

    def get_insults(self):
        # Invocar de forma síncrona al servicio InsultService vía RPC y obtener lista de insultos
        self.insult_response = None
        self.insult_corr_id = str(uuid.uuid4())
        # Publicar petición en la cola 'insult_rpc_queue'
        self.insult_channel.basic_publish(
            exchange='',
            routing_key='insult_rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.insult_corr_id
            ),
            body=''  # Cuerpo vacío (la petición de la lista de insultos)
        )
        # Esperar la respuesta del servicio InsultService
        while self.insult_response is None:
            self.insult_connection.process_data_events(time_limit=None)
        return self.insult_response

    def on_request(self, ch, method, props, body):
        # Callback para procesar peticiones de filtrado de insultos
        texto = body.decode()  # Texto recibido en la petición
        print(f"Recibido texto a filtrar: {texto}")

        # Obtener lista actual de insultos desde el servicio InsultService
        insults = self.get_insults()
        print(f"Lista de insultos recibida: {insults}")

        # Filtrar cada insulto en el texto
        texto_filtrado = texto
        for insulto in insults:
            # Reemplazar cada insulto por 'CENSORED' (se asume coincidencia exacta)
            texto_filtrado = texto_filtrado.replace(insulto, "CENSORED")

        # Publicar la respuesta en la cola indicada por 'reply_to'
        response = texto_filtrado
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=response.encode()
        )
        # Confirmar que se procesó el mensaje original
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Texto filtrado enviado: {texto_filtrado}")

    def start(self):
        print(" [x] Servicio de filtrado de insultos escuchando en 'filter_rpc_queue'")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print(" [!] Interrumpido por el usuario")
            self.channel.stop_consuming()
            self.connection.close()
            self.insult_connection.close()

if __name__ == '__main__':
    service = InsultFilterService()
    service.start()
