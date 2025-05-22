import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("performance_results.csv", names=[
    "clients", "messages", "total_messages", "duration", "throughput", "avg_latency", "p95_latency"
])

plt.figure(figsize=(10, 5))
plt.plot(df['total_messages'], df['throughput'], marker='o', label='Throughput')
plt.title("Throughput vs Total Messages")
plt.xlabel("Mensajes Totales")
plt.ylabel("Throughput (msg/s)")
plt.grid()
plt.tight_layout()
plt.savefig("throughput_vs_messages.png")
plt.show()

plt.figure(figsize=(10, 5))
plt.plot(df['total_messages'], df['duration'], marker='o', color='orange', label='Duración')
plt.title("Duración total vs Total Messages")
plt.xlabel("Mensajes Totales")
plt.ylabel("Duración (segundos)")
plt.grid()
plt.tight_layout()
plt.savefig("duration_vs_messages.png")
plt.show()
