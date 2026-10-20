"""
Paso 3: capturar banners reales del simulador (debe estar corriendo en otra terminal).
Uso: python3 pasos/paso3_captura.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from captura import capturar_banner_tcp, capturar_cabeceras_http  # noqa: E402
from config import DESPLAZAMIENTO, TARGET_HOST  # noqa: E402

print(f"=== Prueba FTP (puerto {21 + DESPLAZAMIENTO}): el servicio habla primero ===")
print(f"Banner: {capturar_banner_tcp(TARGET_HOST, 21 + DESPLAZAMIENTO)[:100]}")

print(f"\n=== Prueba SSH (puerto {22 + DESPLAZAMIENTO}) ===")
print(f"Banner: {capturar_banner_tcp(TARGET_HOST, 22 + DESPLAZAMIENTO)[:100]}")

print(f"\n=== Prueba HTTP (puerto {80 + DESPLAZAMIENTO}): hay que preguntar con HEAD ===")
resultado = capturar_cabeceras_http(TARGET_HOST, 80 + DESPLAZAMIENTO)
print(f"Status: {resultado['status']}")
print(f"Banner: {resultado['banner']}")
print(f"Cabeceras: {resultado['headers']}")
