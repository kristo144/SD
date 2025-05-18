import pika

def on_insult(ch, method, properties, body):
    insult = body.decode('utf-8')
    print(f"Insulto recibido del stream: {insult}")

def subscribe_insults():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='insults_exch', exchange_type='fanout')
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='insults_exch', queue=queue_name)

    print("[ClienteSubscripcion] Suscrito a eventos de insultos. Presione CTRL+C para salir.")
    channel.basic_consume(queue=queue_name, on_message_callback=on_insult, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    subscribe_insults()
