import os, subprocess, time, csv, argparse

# CONFIGURACIÓN POR DEFECTO
NODE_COUNTS = [1,2,3]
CLIENTS    = 10
MESSAGES   = 1500

def launch_servers(n):
    procs = []
    for i in range(n):
        p = subprocess.Popen([
            "gnome-terminal", "--",
            "bash", "-c",
            "python3.13 ../filter_service/filter_server.py"
        ])
        procs.append(p)
    # darles un momento para arrancar
    time.sleep(0.5)
    return procs

def kill_servers(procs):
    for p in procs:
        p.terminate()
    for p in procs:
        p.wait()

def run_test(clients, messages):
    cmd = [
        "python3.13", "performance_test_1node.py",
        "--clients", str(clients),
        "--messages", str(messages)
    ]
    subprocess.run(cmd, check=True)

def main():
    parser = argparse.ArgumentParser(description="Static scaling test para FilterService")
    parser.add_argument("--clients",  type=int, default=CLIENTS)
    parser.add_argument("--messages", type=int, default=MESSAGES)
    parser.add_argument("--nodes", nargs="+", type=int, default=NODE_COUNTS)
    args = parser.parse_args()

    # CSV de resultados
    csv_file = "performance_static_results.csv"
    if not os.path.exists(csv_file):
        with open(csv_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["nodes","clients","messages","total_messages","duration","throughput"])

    for n in args.nodes:
        print(f"\n>>> Probando con {n} nodo(s)...")
        procs = launch_servers(1)

        start = time.time()
        run_test(args.clients, args.messages)
        end = time.time()

        # Leer última línea de performance_results.csv generada por performance_test_1node
        with open("performance_results.csv") as f:
            last = f.readlines()[-1].strip().split(",")
        # [clients,messages,total_messages,duration,throughput,avg_lat,p95]
        _,_,total,dur,thr,_,_ = last

        # Guardar en static CSV
        with open(csv_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([n, args.clients, args.messages, total, dur, thr])

        kill_servers(procs)
        time.sleep(1)

    print("\n>>> Static scaling tests completos. Revisa", csv_file)

if __name__=="__main__":
    main()
