#!/usr/bin/env python3.13
"""
multi_run_performance_test.py

Script en Python para automatizar múltiples ejecuciones del test de rendimiento basado en RabbitMQ RPC.
Este script llama varias veces a performance_test.py con diferentes números de mensajes, captura los resultados
y los consolida en un solo archivo CSV 'resultados_rpc_multiples.csv'.

Características:
1. Ejecutar performance_test.py varias veces con distintos tamaños de carga.
2. Usar subprocess.run() para llamar al script con los parámetros --messages y --length.
3. Capturar los resultados de cada ejecución y agregarlos al archivo CSV consolidado.
4. Formato final del CSV: num_mensajes,tiempo_total_s,throughput_msg_s,latencia_media_s.
5. Código comentado en castellano.
6. Muestra mensajes de progreso en la consola.
"""
import subprocess
import csv
import os
import sys

# Lista de diferentes números de mensajes para probar
message_counts = [100, 500, 1000, 2000]  # Se puede ajustar a otros valores según necesidad

# Tamaño de cada mensaje (payload length).
# Si performance_test.py utiliza este parámetro, se define aquí.
message_length = 100

# Nombre del archivo temporal de resultados generado por performance_test.py
temp_csv = "resultados.csv"
# Nombre del archivo CSV consolidado final
output_csv = "resultados_rpc_multiples.csv"

# Si existe un archivo de resultados consolidado previo, borrarlo para empezar limpio
if os.path.exists(output_csv):
    os.remove(output_csv)

# Escribir el encabezado en el archivo CSV consolidado
with open(output_csv, mode='w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["num_mensajes", "tiempo_total_s", "throughput_msg_s", "latencia_media_s"])

# Ejecutar el test para cada tamaño de carga
for i, count in enumerate(message_counts, start=1):
    print(f"Ejecutando prueba {i}/{len(message_counts)}: {count} mensajes...")

    # Construir el comando para llamar a performance_test.py
    # Se asume que performance_test.py está en el mismo directorio y es ejecutable con python3
    cmd = [
        sys.executable,  # ruta al intérprete Python actual (p. ej. python3.13)
        "performance_test.py",
        "--messages", str(count),
        "--length", str(message_length)
    ]

    try:
        # Ejecutar el comando y capturar la salida (stdout/stderr)
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        # En caso de error, mostrar mensaje y salir
        print(f"Error al ejecutar performance_test.py con {count} mensajes. Código de salida: {e.returncode}")
        print(f"Mensaje de error: {e.stderr}")
        sys.exit(1)

    # Leer los resultados del archivo CSV temporal generado por performance_test.py
    if not os.path.exists(temp_csv):
        print(f"Error: no se encontró el archivo temporal {temp_csv} generado por performance_test.py")
        sys.exit(1)

    with open(temp_csv, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)

    # Asumimos que performance_test.py genera un CSV con una sola línea de datos (más encabezado).
    # Extraer la primera línea de datos (fila 1) si existe
    if len(rows) < 2:
        print(f"Error: el archivo {temp_csv} no contiene datos válidos.")
        sys.exit(1)
    # La primera fila es el encabezado, la segunda es la métrica
    data_row = rows[1]

    # Escribir la fila de datos en el CSV consolidado
    with open(output_csv, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data_row)

    # Mostrar resultados parciales en consola
    num_msgs, total_time, throughput, latencia = data_row
    print(f"-> Resultados: tiempo total = {total_time} s, throughput = {throughput} msg/s, latencia media = {latencia} s\n")

print(f"Pruebas completadas. Resultados consolidados en '{output_csv}'.")
