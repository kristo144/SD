import pika
import threading
import time
import random
import os

# Obtener ruta absoluta del archivo insults.txt
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # un nivel arriba
insults_path = os.path.join(base_dir, 'insults.txt')

with open(insults_path, 'r') as f:
    insults = [line.strip() for line in f if line.strip()]

# Lista local de insultos
insult_list = insults.copy()

def insult_broadcaster():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='insult_broadcast', exchange_type='fanout')
    while True:
        insult = random.choice(insult_list)
        channel.basic_publish(exchange='insult_broadcast', routing_key='', body=insult)
        print(f"Insulto enviado: {insult}")
        time.sleep(5)

def on_request(ch, method, props, body):
    message = body.decode()
    response = ""
    if message.startswith("ADD:"):
        insult = message[4:]
        if insult not in insult_list:
            insult_list.append(insult)
            response = "Insulto añadido."
        else:
            response = "Insulto ya existente."
    elif message == "GET":
        response = '\n'.join(insult_list)
    elif message == "INSULT_ME":
        response = random.choice(insult_list)
    else:
        response = "Comando no reconocido."

    ch.basic_publish(
        exchange='', routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=response)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_server():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='insult_queue') # declaración de la cola de la parte de InsultService
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='insult_queue', on_message_callback=on_request)

        print(" [x] InsultService esperando peticiones en 'insult_queue'...")
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
    finally:
        if not connection.is_closed:
            connection.close()
        print(" [*] Connection closed.")

if __name__ == "__main__":
    # Iniciar el broadcaster en un hilo separado
    threading.Thread(target=insult_broadcaster, daemon=True).start()
    start_server()
