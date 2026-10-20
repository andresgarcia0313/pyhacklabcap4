"""
Paso 4: escanear un solo puerto (SSH) y ver el registro completo que produce el escáner.
Uso: python3 pasos/paso4_un_puerto.py   (con el simulador corriendo)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DESPLAZAMIENTO, TARGET_HOST  # noqa: E402
from escaner import escanear_puerto  # noqa: E402

r = escanear_puerto(TARGET_HOST, 22 + DESPLAZAMIENTO, "SSH")
print(f"Resultado del escaneo del puerto {22 + DESPLAZAMIENTO} (SSH):")
print(json.dumps(r, indent=2, ensure_ascii=False))
