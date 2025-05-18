import pika
import sys

def send_text(text):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='filter_queue')
    channel.basic_publish(exchange='',
                          routing_key='filter_queue',
                          body=text.encode('utf-8'))
    connection.close()
    print(f"[ClienteEnvio] Texto enviado: {text}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python send_text_client.py \"Texto a filtrar\"")
        sys.exit(1)
    text = sys.argv[1]
    send_text(text)
