#!/bin/bash
#
# run_all.sh — lanza NameServer, servidor PyRO y cliente en background
#

# Directorio de trabajo (ajústalo si es necesario)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"

# Crear carpeta de logs
mkdir -p "$LOG_DIR"

echo "=> Iniciando Pyro Name Server..."
nohup python3 -m Pyro4.naming \
    > "$LOG_DIR/ns.log" 2>&1 &
NS_PID=$!
echo "   PID: $NS_PID  Log: $LOG_DIR/ns.log"

sleep 2  # dar tiempo a que se levante

echo "=> Iniciando InsultService Server..."
nohup python3 "$SCRIPT_DIR/insults_service_server.py" \
    > "$LOG_DIR/server.log" 2>&1 &
SRV_PID=$!
echo "   PID: $SRV_PID  Log: $LOG_DIR/server.log"

sleep 2  # dar tiempo a que el servicio se registre

echo "=> Iniciando InsultClient..."
nohup python3 "$SCRIPT_DIR/insult_client.py" \
    > "$LOG_DIR/client.log" 2>&1 &
CLI_PID=$!
echo "   PID: $CLI_PID  Log: $LOG_DIR/client.log"

echo
echo "Todos los procesos están corriendo en segundo plano."
echo "Para seguir sus salidas en tiempo real, ejecuta por ejemplo:"
echo "  tail -f $LOG_DIR/ns.log $LOG_DIR/server.log $LOG_DIR/client.log"
echo
echo "Para detenerlos, puedes usar:"
echo "  kill $NS_PID $SRV_PID $CLI_PID"
