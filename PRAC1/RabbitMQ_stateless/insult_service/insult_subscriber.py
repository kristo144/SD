import pika

def callback(ch, method, properties, body):
    print(f"Insulto recibido: {body.decode()}")

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.exchange_declare(exchange='insult_broadcast', exchange_type='fanout')
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange='insult_broadcast', queue=queue_name)
print(" [*] Esperando insultos. Presione CTRL+C para salir.")
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
channel.start_consuming()
