import pika
import threading
import time
import random
import json

# Lista global de insultos
insults = []

def publish_insults():
    """Envía un insulto aleatorio cada 5 segundos usando un exchange fanout."""
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='insults_exch', exchange_type='fanout')
    while True:
        if insults:
            insult = random.choice(insults)
            channel.basic_publish(exchange='insults_exch', routing_key='', body=insult.encode('utf-8'))
            print(f"[InsultService] Publicado insulto: {insult}")
        time.sleep(5)

def on_request(ch, method, props, body):
    """Callback para manejar peticiones de clientes: añadir insultos o recuperar la lista."""
    global insults
    respuesta = ''
    mensaje = json.loads(body.decode('utf-8'))
    accion = mensaje.get('action')

    if accion == 'add':
        insult = mensaje.get('insult', '').strip()
        if insult:
            if insult not in insults:
                insults.append(insult)
                respuesta = json.dumps({'status': 'OK', 'message': f'Insulto \"{insult}\" añadido.'})
                print(f"[InsultService] Insulto añadido: {insult}")
            else:
                respuesta = json.dumps({'status': 'EXISTS', 'message': 'El insulto ya existe.'})
                print(f"[InsultService] Insulto ya existe: {insult}")
        else:
            respuesta = json.dumps({'status': 'ERROR', 'message': 'Insulto vacío.'})
    elif accion == 'get':
        respuesta = json.dumps({'status': 'OK', 'insults': insults})
        print(f"[InsultService] Lista de insultos enviada.")
    else:
        respuesta = json.dumps({'status': 'ERROR', 'message': 'Acción desconocida.'})

    # Enviar respuesta al cliente usando propiedades reply_to y correlation_id
    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = props.correlation_id),
                     body=respuesta.encode('utf-8'))
    ch.basic_ack(delivery_tag = method.delivery_tag)

def main():
    # Iniciar thread que publica insultos periódicamente
    publisher_thread = threading.Thread(target=publish_insults, daemon=True)
    publisher_thread.start()

    # Configurar RabbitMQ para el servicio de insultos (RPC)
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Cola para recibir peticiones RPC (add/get)
    channel.queue_declare(queue='insult_rpc_queue')
    channel.basic_qos(prefetch_count=1)  # Procesar una petición a la vez
    channel.basic_consume(queue='insult_rpc_queue', on_message_callback=on_request)

    print("[InsultService] Esperando peticiones. CTRL+C para salir.")
    channel.start_consuming()

if __name__ == '__main__':
    main()
