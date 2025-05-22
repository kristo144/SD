import pika
import uuid

def insult_me():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    corr_id = str(uuid.uuid4())
    channel.basic_publish(
        exchange='',
        routing_key='insult_queue',
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=corr_id,
        ),
        body="INSULT_ME"
    )

    def on_response(ch, method, props, body):
        if corr_id == props.correlation_id:
            print(f"Insulto recibido: {body.decode()}")
            ch.stop_consuming()

    channel.basic_consume(queue=callback_queue, on_message_callback=on_response, auto_ack=True)
    channel.start_consuming()
    connection.close()

if __name__ == "__main__":
    insult_me()
