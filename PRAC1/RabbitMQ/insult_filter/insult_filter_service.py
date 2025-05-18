import pika
import json
import time
import uuid

# Lista de resultados filtrados
filtered_texts = []

def get_current_insults():
    """Obtiene la lista de insultos actual desde InsultService mediante RPC."""
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Crear cola exclusiva para recibir la respuesta
    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    corr_id = str(uuid.uuid4())
    # Enviar petición de obtención de insultos
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
            break
        time.sleep(0.01)
    connection.close()
    return insults

def process_text(ch, method, props, body):
    """Callback para procesar textos: filtra insultos y guarda el resultado."""
    texto = body.decode('utf-8')
    print(f"[InsultFilter] Texto recibido para filtrar: {texto}")
    insults = get_current_insults()
    texto_filtrado = texto
    for insult in insults:
        texto_filtrado = texto_filtrado.replace(insult, "CENSORED")
    filtered_texts.append(texto_filtrado)
    print(f"[InsultFilter] Texto filtrado: {texto_filtrado}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def on_request(ch, method, props, body):
    """Callback para responder a las consultas de resultados filtrados."""
    mensaje = json.loads(body.decode('utf-8'))
    accion = mensaje.get('action')
    if accion == 'get':
        respuesta = json.dumps({'status': 'OK', 'filtered': filtered_texts})
    else:
        respuesta = json.dumps({'status': 'ERROR', 'message': 'Acción desconocida.'})
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = props.correlation_id),
                     body=respuesta.encode('utf-8'))
    ch.basic_ack(delivery_tag = method.delivery_tag)

def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Cola para recibir textos a filtrar (work queue)
    channel.queue_declare(queue='filter_queue')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='filter_queue', on_message_callback=process_text)

    # Cola para consultas RPC de resultados
    channel.queue_declare(queue='filter_rpc_queue')
    channel.basic_consume(queue='filter_rpc_queue', on_message_callback=on_request)

    print("[InsultFilter] Esperando mensajes. CTRL+C para salir.")
    channel.start_consuming()

if __name__ == '__main__':
    main()
