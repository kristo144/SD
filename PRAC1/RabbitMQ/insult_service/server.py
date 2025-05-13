import pika
import json
import threading
import time
import random
import uuid
from model import InsultService

"""
    Implementación del servicio de insultos usando RabbitMQ para su exposición remota.
    Incluye un broadcaster que envía insultos aleatorios a los suscriptores cada 5 segundos.
"""

class RabbitMQInsultServer:
    def __init__(self):
        # Crear la instancia del servicio de insultos
        self.service = InsultService()
        
        # Configurar la conexión RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        
        # Declarar colas para solicitudes y respuestas
        self.channel.queue_declare(queue='insult_service_requests')
        
        # Cola para emisiones (broadcast)
        self.channel.exchange_declare(exchange='insult_broadcast', exchange_type='fanout')
        
        # Iniciar el broadcaster en un hilo separado
        self.running = True
        self.broadcast_thread = threading.Thread(target=self._broadcaster)
        self.broadcast_thread.daemon = True
        self.broadcast_thread.start()
        
        # Configurar el consumidor de solicitudes
        self.channel.basic_consume(
            queue='insult_service_requests',
            on_message_callback=self._process_request,
            auto_ack=True
        )

    def _process_request(self, ch, method, properties, body):
        """
        Procesa las solicitudes recibidas y envía respuestas
        """
        request = json.loads(body)
        action = request.get('action')
        response = {'success': False, 'error': 'Acción desconocida'}
        
        # Procesar según la acción solicitada
        if action == 'add_insult':
            insult = request.get('insult', '')
            success = self.service.add_insult(insult)
            response = {'success': success}
            
        elif action == 'get_insults':
            insults = self.service.get_insults()
            response = {'success': True, 'insults': insults}
            
        elif action == 'subscribe':
            subscriber_id = request.get('subscriber_id', '')
            success = self.service.subscribe(subscriber_id)
            response = {'success': success}
            
        elif action == 'unsubscribe':
            subscriber_id = request.get('subscriber_id', '')
            success = self.service.unsubscribe(subscriber_id)
            response = {'success': success}
            
        elif action == 'get_subscribers':
            subscribers = self.service.get_subscribers()
            response = {'success': True, 'subscribers': subscribers}
        
        # Enviar respuesta al cliente
        if properties.reply_to:
            ch.basic_publish(
                exchange='',
                routing_key=properties.reply_to,
                properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                body=json.dumps(response)
            )
    
    def _broadcaster(self):
        """
        Method que se ejecuta en un hilo separado y envía insultos aleatorios
        a los suscriptores cada 5 segundos
        """
        while self.running:
            time.sleep(5)  # pausa de 5 segundos
            
            # Verificar si hay insultos y suscriptores
            insults = self.service.get_insults()
            subscribers = self.service.get_subscribers()
            
            if not insults or not subscribers:
                continue
                
            # Seleccionar un insulto aleatorio
            random_insult = random.choice(insults)
            
            # Enviar a todos los suscriptores mediante el exchange fanout
            message = {
                'type': 'broadcast',
                'insult': random_insult,
                'timestamp': time.time()
            }
            
            self.channel.basic_publish(
                exchange='insult_broadcast',
                routing_key='',  # No se necesita con fanout
                body=json.dumps(message)
            )
            
            print(f"Broadcasted insult: {random_insult} to {len(subscribers)} subscribers")
    
    def start(self):
        """
        Inicia el servidor y espera por solicitudes
        """
        print("Iniciando servidor InsultService (RabbitMQ)...")
        print("Esperando solicitudes...")
        
        try:
            # Iniciar el consumo de mensajes
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.running = False
            self.connection.close()
            print("Servidor detenido.")


def start_server():
    """
    Función principal para iniciar el servidor
    """
    server = RabbitMQInsultServer()
    server.start()


if __name__ == "__main__":
    start_server()
