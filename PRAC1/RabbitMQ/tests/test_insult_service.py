import pika
import uuid
import json
import time

print("[Test InsultService] Iniciando prueba del servicio de insultos.")

# Función auxiliar para solicitar al servicio
def call_insult_service(request):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue
    corr_id = str(uuid.uuid4())
    channel.basic_publish(exchange='',
                          routing_key='insult_rpc_queue',
                          properties=pika.BasicProperties(
                              reply_to=callback_queue,
                              correlation_id=corr_id
                          ),
                          body=json.dumps(request).encode('utf-8'))
    while True:
        method_frame, props, body = channel.basic_get(queue=callback_queue, auto_ack=True)
        if method_frame and props.correlation_id == corr_id:
            response = json.loads(body.decode('utf-8'))
            connection.close()
            return response

# Probar añadir insultos
for insult in ["tonto", "idiota", "tonto"]:
    print(f"Añadiendo insulto: {insult}")
    resp = call_insult_service({'action': 'add', 'insult': insult})
    print(f"Respuesta: {resp.get('message')}")

# Probar obtener lista
print("Obteniendo lista de insultos...")
resp = call_insult_service({'action': 'get'})
insults = resp.get('insults', [])
print(f"Insultos recibidos ({len(insults)}): {insults}")
