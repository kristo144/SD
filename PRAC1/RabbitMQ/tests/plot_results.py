#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import matplotlib.pyplot as plt

# Listas para almacenar los datos del CSV
num_msgs = []
throughputs = []
latencies = []

# Leer el CSV con los nombres reales de las columnas
with open('resultados.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        num_msgs.append(int(row['num_mensajes']))
        throughputs.append(float(row['throughput_msg_s']))
        latencies.append(float(row['latencia_media_s']))

# Gráfica: Throughput vs Número de mensajes
plt.figure()
plt.plot(num_msgs, throughputs, marker='o')
plt.xlabel('Número de mensajes')
plt.ylabel('Throughput (mensajes/s)')
plt.title('Throughput vs Número de mensajes')
plt.grid(True)
plt.tight_layout()
plt.savefig('throughput_vs_msgs.png')
print("Gráfica throughput_vs_msgs.png generada.")

# Gráfica: Latencia media vs Número de mensajes
plt.figure()
plt.plot(num_msgs, latencies, marker='o')
plt.xlabel('Número de mensajes')
plt.ylabel('Latencia media (s)')
plt.title('Latencia media vs Número de mensajes')
plt.grid(True)
plt.tight_layout()
plt.savefig('latency_vs_msgs.png')
print("Gráfica latency_vs_msgs.png generada.")
