"""
Paso 5: probar el resumen en consola con datos de ejemplo (sin red).
Uso: python3 pasos/paso5_reporte.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from report import imprimir_resumen_consola  # noqa: E402

datos_prueba = [
    {"port": 10021, "service": "ProFTPD", "version": "1.3.3c", "risk": "CRITICAL", "http_status": None},
    {"port": 10022, "service": "OpenSSH", "version": "4.7p1", "risk": "HIGH", "http_status": None},
    {"port": 10080, "service": "Apache", "version": "2.2.8", "risk": "HIGH", "http_status": 200},
]
imprimir_resumen_consola(datos_prueba, "127.0.0.1")
