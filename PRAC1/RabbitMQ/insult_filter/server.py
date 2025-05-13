import pika
import json
import threading
from model import InsultFilter

"""
    Implementación del servicio de filtrado de insultos usando RabbitMQ.
    Permite filtrar textos consultando la lista de insultos del InsultService.
"""

class RabbitMQFilterServer:
    def __init__(self):
        # Crear la instancia del filtro
        self.filter = InsultFilter()
        
        # Configurar la conexión RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        
        # Declarar cola para solicitudes de filtrado
        self.channel.queue_declare(queue='filter_service_requests')
        
        # Configurar el consumidor de solicitudes
        self.channel.basic_consume(
            queue='filter_service_requests',
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
        
        if action == 'filter_text':
            # Conectar con el servicio de insultos para obtener la lista actual
            insult_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            insult_channel = insult_connection.channel()
            
            # Cola para recibir respuesta del servicio de insultos
            result = insult_channel.queue_declare(queue='', exclusive=True)
            callback_queue = result.method.queue
            
            corr_id = properties.correlation_id
            
            # Solicitar lista de insultos
            insult_request = {
                'action': 'get_insults'
            }
            
            # Variables para almacenar la respuesta del servicio de insultos
            insults_response = None
            
            # Callback para recibir la respuesta del servicio de insultos
            def on_response(ch2, method2, props2, body2):
                nonlocal insults_response
                if props2.correlation_id == corr_id:
                    insults_response = json.loads(body2)
                    
            # Configurar el consumidor para la respuesta
            insult_channel.basic_consume(
                queue=callback_queue,
                on_message_callback=on_response,
                auto_ack=True
            )
            
            # Publicar solicitud al servicio de insultos
            insult_channel.basic_publish(
                exchange='',
                routing_key='insult_service_requests',
                properties=pika.BasicProperties(
                    reply_to=callback_queue,
                    correlation_id=corr_id,
                ),
                body=json.dumps(insult_request)
            )
            
            # Esperar la respuesta (con timeout)
            start_time = insult_connection.time()
            while insults_response is None and (insult_connection.time() - start_time < 5):
                insult_connection.process_data_events()
                
            # Si obtuvimos la lista de insultos, filtrar el texto
            insults = []
            if insults_response and insults_response.get('success'):
                insults = insults_response.get('insults', [])
                
            # Filtrar el texto
            text = request.get('text', '')
            filtered_text = self.filter.filter_text(text, insults)
            response = {'success': True, 'filtered_text': filtered_text}
            
            # Cerrar la conexión temporal
            insult_connection.close()
            
        elif action == 'get_filtered_texts':
            filtered_texts = self.filter.get_filtered_texts()
            response = {'success': True, 'filtered_texts': filtered_texts}
        
        # Enviar respuesta al cliente
        if properties.reply_to:
            ch.basic_publish(
                exchange='',
                routing_key=properties.reply_to,
                properties=pika.BasicProperties(correlation_id=properties.correlation_id),
                body=json.dumps(response)
            )
    
    def start(self):
        """
        Inicia el servidor y espera por solicitudes
        """
        print("Iniciando servidor InsultFilter (RabbitMQ)...")
        print("Esperando solicitudes...")
        
        try:
            # Iniciar el consumo de mensajes
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()
            print("Servidor detenido.")


def start_server():
    """
    Función principal para iniciar el servidor
    """
    server = RabbitMQFilterServer()
    server.start()


if __name__ == "__main__":
    start_server()
