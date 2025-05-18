import pika
import sys
import json
import uuid
import time

def add_insult(insult):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    corr_id = str(uuid.uuid4())
    request = {'action': 'add', 'insult': insult}
    channel.basic_publish(exchange='',
                          routing_key='insult_rpc_queue',
                          properties=pika.BasicProperties(
                              reply_to=callback_queue,
                              correlation_id=corr_id
                          ),
                          body=json.dumps(request).encode('utf-8'))

    # Esperar respuesta
    while True:
        method_frame, props, body = channel.basic_get(queue=callback_queue, auto_ack=True)
        if method_frame and props.correlation_id == corr_id:
            respuesta = json.loads(body.decode('utf-8'))
            connection.close()
            return respuesta
        time.sleep(0.01)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python add_insult_client.py \"Insulto a añadir\"")
        sys.exit(1)
    insult = sys.argv[1]
    resp = add_insult(insult)
    print(f"Respuesta del servicio: {resp.get('message')}")
