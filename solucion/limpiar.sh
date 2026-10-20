#!/usr/bin/env bash
# Sección 9: deja el entorno limpio. Detiene el simulador si quedó corriendo.
# Uso: ./limpiar.sh                   (conserva los reportes)
#      ./limpiar.sh --borrar-reportes (además borra output/*.json)
set -euo pipefail
cd "$(dirname "$0")"

if pkill -f '^python[0-9.]* (\./)?simulador_metasploitable\.py'; then
  for _ in $(seq 1 20); do  # espera hasta 5 s a que el proceso termine
    pgrep -f '^python[0-9.]* (\./)?simulador_metasploitable\.py' >/dev/null || break
    sleep 0.25
  done
  echo "[+] Simulador detenido"
else
  echo "[=] El simulador no estaba corriendo"
fi

if [[ "${1:-}" == "--borrar-reportes" && -d output ]]; then
  find output -maxdepth 1 -name 'banner_report_*.json' -print -delete
  echo "[+] Reportes borrados"
else
  echo "[=] Reportes conservados en output/ (trátelos como datos sensibles)"
fi

pgrep -af '^python[0-9.]* (\./)?(simulador_metasploitable|banner_grabber)\.py' || echo "[+] Sin procesos del laboratorio activos"
