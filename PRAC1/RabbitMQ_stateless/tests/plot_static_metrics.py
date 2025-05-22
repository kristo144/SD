import pandas as pd
import matplotlib.pyplot as plt
import os

csv_path = "performance_static_results.csv"
if not os.path.exists(csv_path):
    print("Error: no existe", csv_path); exit(1)

df = pd.read_csv(csv_path)

# Calcular speedup basado en duración
t1 = df.loc[df['nodes']==1, 'duration'].values[0]
df['speedup'] = t1 / df['duration']

# Throughput vs Nodos
plt.figure(figsize=(8,5))
plt.plot(df['nodes'], df['throughput'], marker='o')
plt.title("Throughput vs Número de Nodos")
plt.xlabel("Nodos")
plt.ylabel("Throughput (msg/s)")
plt.grid(True)
plt.tight_layout()
plt.savefig("throughput_vs_nodes.png")
plt.show()

# Speedup vs Nodos
plt.figure(figsize=(8,5))
plt.plot(df['nodes'], df['speedup'], marker='o')
plt.title("Speedup estático vs Número de Nodos")
plt.xlabel("Nodos")
plt.ylabel("Speedup (T1/Tn)")
plt.grid(True)
plt.tight_layout()
plt.savefig("speedup_vs_nodes.png")
plt.show()
