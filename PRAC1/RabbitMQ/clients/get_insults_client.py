import pika
import json
import uuid
import time

def get_insults():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    corr_id = str(uuid.uuid4())
    request = {'action': 'get'}
    channel.basic_publish(exchange='',
                          routing_key='insult_rpc_queue',
                          properties=pika.BasicProperties(
                              reply_to=callback_queue,
                              correlation_id=corr_id
                          ),
                          body=json.dumps(request).encode('utf-8'))

    insults = []
    while True:
        method_frame, props, body = channel.basic_get(queue=callback_queue, auto_ack=True)
        if method_frame and props.correlation_id == corr_id:
            response = json.loads(body.decode('utf-8'))
            insults = response.get('insults', [])
            connection.close()
            return insults
        time.sleep(0.01)

if __name__ == '__main__':
    insults = get_insults()
    print("Insultos actuales:")
    for insult in insults:
        print(f" - {insult}")
