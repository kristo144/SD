import pika
import os

# Obtener ruta absoluta del archivo insults.txt
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # un nivel arriba
insults_path = os.path.join(base_dir, 'insults.txt')

with open(insults_path, 'r') as f:
    insults = [line.strip() for line in f if line.strip()]

# Lista local de textos filtrados (no compartida con otros servidores)
filtered_texts = []

def filter_text(text):
    """
    Función que reemplaza cualquier insulto encontrado en el texto con la palabra 'CENSORED'
    """
    words = text.split()
    filtered = ' '.join(['CENSORED' if word in insults else word for word in words])
    filtered_texts.append(filtered)
    print(f"Texto recibido: {text}")
    print(f"Texto filtrado: {filtered}")

def on_request(ch, method, props, body):
    """
    Callback que gestiona las peticiones recibidas por la cola.
    - FILTER:<texto>: filtra el texto y lo guarda.
    - GET: devuelve todos los textos filtrados.
    """
    message = body.decode()
    response = ""

    if message.startswith("FILTER:"):
        text = message[len("FILTER:"):]
        filter_text(text)
        response = "Texto filtrado y almacenado."
    elif message == "GET":
        response = '\n'.join(filtered_texts)
    else:
        response = "Comando no reconocido."

    if props.reply_to:
        ch.basic_publish(
            exchange='',
            routing_key=str(props.reply_to),
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=response
        )
    else:
        print("Error: 'reply_to' not defined or NONE")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_server():
    """
    Inicializa el servidor, conecta a RabbitMQ y escucha la cola 'filter_queue'.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='filter_queue')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='filter_queue', on_message_callback=on_request)

    print(" [x] FilterService esperando peticiones en 'filter_queue'.")
    channel.start_consuming()

if __name__ == "__main__":
    start_server()
