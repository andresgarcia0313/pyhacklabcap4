"""
Paso 1: revisar la configuración central (config.py).
Uso (desde la carpeta paso-a-paso/): python3 pasos/paso1_configuracion.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402  (va después de ajustar sys.path)

print(f"Objetivo (TARGET_HOST): {config.TARGET_HOST}")
print(f"Lista permitida (HOSTS_PERMITIDOS): {sorted(config.HOSTS_PERMITIDOS)}")
print(f"\n{'Servicio':<10} {'Puerto estándar':>15} {'Puerto local':>13}")
for puerto_estandar, servicio in config.PUERTOS_ESTANDAR.items():
    print(f"{servicio:<10} {puerto_estandar:>15} {puerto_estandar + config.DESPLAZAMIENTO:>13}")
print(f"\nServicios que se consultan por HTTP: {sorted(config.SERVICIOS_HTTP)}")
print(f"Hilos paralelos: {config.MAX_WORKERS} | Timeout TCP: {config.SOCKET_TIMEOUT}s")
