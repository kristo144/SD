import pika
import uuid
import json
import time

def get_filtered_results():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    corr_id = str(uuid.uuid4())
    request = {'action': 'get'}
    channel.basic_publish(exchange='',
                          routing_key='filter_rpc_queue',
                          properties=pika.BasicProperties(
                              reply_to=callback_queue,
                              correlation_id=corr_id
                          ),
                          body=json.dumps(request).encode('utf-8'))

    results = []
    while True:
        method_frame, props, body = channel.basic_get(queue=callback_queue, auto_ack=True)
        if method_frame and props.correlation_id == corr_id:
            response = json.loads(body.decode('utf-8'))
            results = response.get('filtered', [])
            connection.close()
            return results
        time.sleep(0.01)

if __name__ == '__main__':
    results = get_filtered_results()
    print("Resultados filtrados:")
    for r in results:
        print(f" - {r}")
