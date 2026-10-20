#!/usr/bin/env bash
# Ejecuta el laboratorio 4 completo en local y se detiene en el primer fallo:
# entorno -> pruebas -> simulador -> escaneo -> validación 7.x -> Problema 2 -> limpieza.
# Uso: ./ejecutar_laboratorio.sh
set -euo pipefail
cd "$(dirname "$0")"

# Archivos que construye el estudiante y el paso de la guía que los crea
faltan=0
for par in config.py:1 signatures.py:2 captura.py:3 escaner.py:4 report.py:5 banner_grabber.py:6; do
  if [[ ! -f "${par%%:*}" ]]; then
    echo "[!] Falta ${par%%:*}: se crea en el Paso ${par##*:} de la guía"
    faltan=1
  fi
done
[[ $faltan -eq 0 ]] || exit 1

PID_SIM=""
detener_simulador() {
  if [[ -n "$PID_SIM" ]] && kill -0 "$PID_SIM" 2>/dev/null; then
    kill "$PID_SIM" && wait "$PID_SIM" 2>/dev/null || true
  fi
  PID_SIM=""
}
trap detener_simulador EXIT

puerto_ssh_abierto() {
  python3 -c "import socket; socket.create_connection(('127.0.0.1', 10022), 1)" 2>/dev/null
}

iniciar_simulador() {
  if puerto_ssh_abierto; then  # otro simulador u otro programa ocupa los puertos
    echo "[!] El puerto 10022 ya está en uso. Ejecute ./limpiar.sh y vuelva a intentarlo."; exit 1
  fi
  python3 simulador_metasploitable.py "$@" &
  PID_SIM=$!
  for _ in $(seq 1 20); do  # espera hasta 5 s a que abra el puerto SSH simulado
    if puerto_ssh_abierto && kill -0 "$PID_SIM" 2>/dev/null; then return 0; fi
    sleep 0.25
  done
  echo "[!] El simulador no arrancó"; exit 1
}

titulo() { printf '\n========== %s ==========\n' "$1"; }

titulo "Paso 0: entorno virtual y dependencias"
# --system-site-packages reutiliza requests si ya está instalado (funciona sin Internet)
[[ -d .venv ]] || python3 -m venv --system-site-packages .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python3 -m pip install -q -r requirements.txt
python3 -c "import socket, requests, re, concurrent.futures, json; print('Dependencias OK, requests', requests.__version__)"

titulo "Pruebas automáticas (sin simulador: cada prueba levanta sus propios servicios)"
python3 -m unittest test_firmas test_captura_local test_seguridad

titulo "Paso 6: simulador + escaneo completo"
iniciar_simulador
python3 banner_grabber.py

titulo "Sección 7: validación del reporte"
python3 validar.py

titulo "Problema 2: el servidor web rechaza HEAD"
detener_simulador
iniciar_simulador --rechazar-head
echo "[*] curl -I (HEAD) contra el puerto 10080:"
curl -sS -I --max-time 3 http://127.0.0.1:10080/ || echo "    -> HEAD falló, como en el Problema 2"
echo "[*] La herramienta reintenta con GET y aun así identifica el servicio:"
python3 -c "from escaner import escanear_puerto; r = escanear_puerto('127.0.0.1', 10080, 'HTTP'); print('   ', r['service'], r['version'], r['risk'], r['http_status'])"
detener_simulador

titulo "Sección 9: limpieza"
pgrep -af '^python[0-9.]* (\./)?(simulador_metasploitable|banner_grabber)\.py' || echo "Sin procesos del laboratorio activos"
echo "Reportes generados (datos sensibles, no se suben al repositorio):"
ls -1 output/*.json
echo; echo "LABORATORIO COMPLETADO"
