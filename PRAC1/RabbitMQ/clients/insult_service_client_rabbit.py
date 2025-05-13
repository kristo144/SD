import pika
import json
import uuid
import sys


class InsultServiceClient:
    def __init__(self):
        # Configurar la conexión RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        
        # Crear una cola exclusiva para recibir respuestas
        result = self.channel.queue_declare(queue='', exclusive=True)
        self.callback_queue = result.method.queue
        
        # Configurar el consumidor de respuestas
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True
        )
        
        # Para almacenar las respuestas recibidas
        self.response = None
        self.corr_id = None
        
        # ID único para este cliente (para suscripciones)
        self.client_id = str(uuid.uuid4())
        
        # Estado de suscripción
        self.subscribed = False
        
        # Configurar el canal para recibir broadcasts si nos suscribimos
        self.subscribe_channel = None
        self.subscribe_connection = None
    
    def _on_response(self, ch, method, props, body):
        """
        Callback para procesar respuestas a solicitudes
        """
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)
    
    def _call(self, request):
        """
        Método para hacer llamadas RPC al servicio
        """
        self.response = None
        self.corr_id = str(uuid.uuid4())
        
        # Enviar solicitud
        self.channel.basic_publish(
            exchange='',
            routing_key='insult_service_requests',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(request)
        )
        
        # Esperar la respuesta
        while self.response is None:
            self.connection.process_data_events()
            
        return self.response
    
    def add_insult(self, insult):
        """
        Añade un insulto al servicio
        """
        request = {
            'action': 'add_insult',
            'insult': insult
        }
        response = self._call(request)
        return response.get('success', False)
    
    def get_insults(self):
        """
        Obtiene la lista de insultos del servicio
        """
        request = {
            'action': 'get_insults'
        }
        response = self._call(request)
        return response.get('insults', []) if response.get('success', False) else []
    
    def subscribe(self):
        """
        Suscribe al cliente para recibir notificaciones de insultos aleatorios
        """
        if self.subscribed:
            print("Ya estás suscrito a las notificaciones")
            return True
        
        # Primero registramos la suscripción en el servicio
        request = {
            'action': 'subscribe',
            'subscriber_id': self.client_id
        }
        response = self._call(request)
        
        if response.get('success', False):
            # Ahora configuramos la conexión para recibir broadcasts
            self.subscribe_connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
            self.subscribe_channel = self.subscribe_connection.channel()
            
            # Declarar el exchange para broadcast
            self.subscribe_channel.exchange_declare(exchange='insult_broadcast', exchange_type='fanout')
            
            # Crear una cola temporal exclusiva
            result = self.subscribe_channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            
            # Vincular la cola al exchange
            self.subscribe_channel.queue_bind(exchange='insult_broadcast', queue=queue_name)
            
            # Configurar el consumidor para recibir broadcasts
            self.subscribe_channel.basic_consume(
                queue=queue_name,
                on_message_callback=self._on_broadcast,
                auto_ack=True
            )
            
            # Iniciar un hilo para consumir mensajes
            import threading
            self.subscribe_thread = threading.Thread(target=self._consume_broadcasts)
            self.subscribe_thread.daemon = True
            self.subscribe_thread.start()
            
            self.subscribed = True
            return True
        
        return False
    
    def _on_broadcast(self, ch, method, properties, body):
        """
        Callback para procesar mensajes de broadcast
        """
        try:
            message = json.loads(body)
            if message.get('type') == 'broadcast':
                print(f"\n[RANDOM INSULT]: {message.get('insult')}")
        except Exception as e:
            print(f"Error al procesar broadcast: {e}")
    
    def _consume_broadcasts(self):
        """
        Método para consumir broadcasts en un hilo separado
        """
        try:
            self.subscribe_channel.start_consuming()
        except Exception as e:
            print(f"Error en consumo de broadcasts: {e}")
            self.subscribed = False
    
    def unsubscribe(self):
        """
        Cancela la suscripción a notificaciones
        """
        if not self.subscribed:
            print("No estás suscrito a las notificaciones")
            return True
        
        request = {
            'action': 'unsubscribe',
            'subscriber_id': self.client_id
        }
        response = self._call(request)
        
        if response.get('success', False):
            # Detener el consumo de broadcasts
            if self.subscribe_channel:
                try:
                    self.subscribe_channel.stop_consuming()
                    self.subscribe_connection.close()
                except:
                    pass
            
            self.subscribed = False
            return True
        
        return False
    
    def get_subscribers(self):
        """
        Obtiene la lista de suscriptores
        """
        request = {
            'action': 'get_subscribers'
        }
        response = self._call(request)
        return response.get('subscribers', []) if response.get('success', False) else []
    
    def close(self):
        """
        Cierra la conexión con el servicio
        """
        if self.subscribed:
            self.unsubscribe()
        
        if self.connection:
            self.connection.close()


def main():
    try:
        # Crear el cliente
        client = InsultServiceClient()
        
        # Flag para mantener la ejecución del programa
        running = True
        
        print("Cliente del Servicio de Insultos (RabbitMQ)")
        print("---------------------------------------")
        
        while running:
            print("\nOpciones:")
            print("1. Añadir insulto")
            print("2. Ver todos los insultos")
            print("3. Suscribirse a notificaciones")
            print("4. Cancelar suscripción")
            print("5. Ver suscriptores activos")
            print("6. Salir")
            
            choice = input("\nSelecciona una opción (1-6): ")
            
            if choice == "1":
                insult = input("Introduce el insulto a añadir: ")
                if client.add_insult(insult):
                    print(f"Insulto '{insult}' añadido correctamente")
                else:
                    print(f"El insulto '{insult}' ya existe o es inválido")
                    
            elif choice == "2":
                insults = client.get_insults()
                if insults:
                    print("\nLista de insultos:")
                    for idx, insult in enumerate(insults, 1):
                        print(f"{idx}. {insult}")
                else:
                    print("No hay insultos almacenados")
                    
            elif choice == "3":
                if client.subscribe():
                    print("Te has suscrito a las notificaciones de insultos aleatorios")
                else:
                    print("Error al suscribirse")
                    
            elif choice == "4":
                if client.unsubscribe():
                    print("Has cancelado tu suscripción")
                else:
                    print("Error al cancelar la suscripción")
                    
            elif choice == "5":
                subscribers = client.get_subscribers()
                if subscribers:
                    print("\nSuscriptores activos:")
                    for idx, subscriber_id in enumerate(subscribers, 1):
                        status = "TÚ" if subscriber_id == client.client_id else ""
                        print(f"{idx}. {subscriber_id} {status}")
                else:
                    print("No hay suscriptores activos")
                    
            elif choice == "6":
                running = False
                print("Saliendo...")
                client.close()
                
            else:
                print("Opción no válida, intenta de nuevo")
                
    except KeyboardInterrupt:
        print("\nSaliendo...")
        if 'client' in locals():
            client.close()
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
