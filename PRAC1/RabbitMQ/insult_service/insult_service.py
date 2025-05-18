#!/usr/bin/env python3.13

import pika
import threading
import time
import random
import json

# Lista global de insultos
insultos = []

def publish_insults():
    """Publica un insulto aleatorio cada 5 segundos en un exchange fanout."""
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.exchange_declare(exchange='insults_exch', exchange_type='fanout')
    while True:
        if insultos:
            insult = random.choice(insultos)
            channel.basic_publish(exchange='insults_exch', routing_key='', body=insult.encode('utf-8'))
            print(f"[InsultService] Publicado insulto: {insult}")
        time.sleep(5)

def on_request(ch, method, props, body):
    """
    Callback para manejar peticiones RPC de add/get insultos.
    Ahora maneja casos en que `body` esté vacío o no sea JSON válido.
    """
    global insultos

    # Intentar parsear body como JSON; si falla o es vacío, asumimos 'get'
    try:
        texto = body.decode('utf-8').strip()
        if texto:
            mensaje = json.loads(texto)
        else:
            mensaje = {'action': 'get'}
    except json.JSONDecodeError:
        # Cuerpo no es JSON: tratamos como petición 'get'
        mensaje = {'action': 'get'}

    accion = mensaje.get('action')
    respuesta = {}

    if accion == 'add':
        insult = mensaje.get('insult', '').strip()
        if insult:
            if insult not in insultos:
                insultos.append(insult)
                respuesta = {'status': 'OK', 'message': f'Insulto \"{insult}\" añadido.'}
                print(f"[InsultService] Insulto añadido: {insult}")
            else:
                respuesta = {'status': 'EXISTS', 'message': 'El insulto ya existe.'}
        else:
            respuesta = {'status': 'ERROR', 'message': 'Insulto vacío.'}

    elif accion == 'get':
        respuesta = {'status': 'OK', 'insultos': insultos}
        print(f"[InsultService] Lista de insultos enviada: {insultos}")

    else:
        respuesta = {'status': 'ERROR', 'message': 'Acción desconocida.'}

    # Responder al cliente usando reply_to y correlation_id
    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(correlation_id=props.correlation_id),
        body=json.dumps(respuesta).encode('utf-8')
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    # Inicia el hilo que publica insultos periódicamente
    publisher = threading.Thread(target=publish_insults, daemon=True)
    publisher.start()

    # Configurar RabbitMQ para peticiones RPC de insultos
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='insult_rpc_queue')
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='insult_rpc_queue', on_message_callback=on_request)

    print("[InsultService] Esperando peticiones en 'insult_rpc_queue'. CTRL+C para salir.")
    channel.start_consuming()

if __name__ == '__main__':
    main()
