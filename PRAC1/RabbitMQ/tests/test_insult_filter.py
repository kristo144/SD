import pika
import uuid
import json
import time

print("[Test InsultFilter] Iniciando prueba del servicio de filtrado de insultos.")

# Funciones auxiliares
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

def send_text_to_filter(text):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.basic_publish(exchange='',
                          routing_key='filter_queue',
                          body=text.encode('utf-8'))
    connection.close()

def get_filtered_results():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue
    corr_id = str(uuid.uuid4())
    channel.basic_publish(exchange='',
                          routing_key='filter_rpc_queue',
                          properties=pika.BasicProperties(
                              reply_to=callback_queue,
                              correlation_id=corr_id
                          ),
                          body=json.dumps({'action': 'get'}).encode('utf-8'))
    while True:
        method_frame, props, body = channel.basic_get(queue=callback_queue, auto_ack=True)
        if method_frame and props.correlation_id == corr_id:
            response = json.loads(body.decode('utf-8'))
            connection.close()
            return response.get('filtered', [])

# Asegurarse de que hay insultos en el servicio
for insult in ["tonto", "idiota", "weon", "caraculo", "Kuliao"]:
    call_insult_service({'action': 'add', 'insult': insult})

# Enviar texto para filtrar
text_to_send1 = "Eres tonto y un idiota"
print(f"Enviando texto para filtrar: \"{text_to_send1}\"")
send_text_to_filter(text_to_send1)
time.sleep(1)

text_to_send2 = "Vaya weon estas hecho, pedazo tonto"
print(f"Enviando texto para filtrar: \"{text_to_send2}\"")
send_text_to_filter(text_to_send2)
time.sleep(1)

text_to_send3 = "acá pareces bastante caraculo.Además de un poco Kuliao"
print(f"Enviando texto para filtrar: \"{text_to_send3}\"")
send_text_to_filter(text_to_send3)
time.sleep(1)

# Obtener resultados
results = get_filtered_results()
print(f"Resultados recibidos ({len(results)}):")
for idx, texto in enumerate(results, 1):
    print(f" {idx}: {texto}")
