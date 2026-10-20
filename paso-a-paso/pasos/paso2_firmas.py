"""
Paso 2: probar el diccionario de firmas sin red (solo expresiones regulares).
Uso: python3 pasos/paso2_firmas.py
Pruebe a agregar sus propios banners a la lista y observe qué firma gana.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from signatures import clasificar_banner  # noqa: E402

BANNERS_DE_PRUEBA = [
    "220 ProFTPD 1.3.3c Server (Metasploitable)",
    "SSH-2.0-OpenSSH_4.7p1 Debian-8ubuntu1",
    "Apache/2.2.8 (Ubuntu) DAV/2",
    "220 metasploitable.localdomain ESMTP Postfix (Ubuntu)",  # empieza por 220, como FTP
    "SSH-2.0-OpenSSH_10.2p1 Ubuntu-2",                        # versión reciente: riesgo LOW
]

for banner in BANNERS_DE_PRUEBA:
    r = clasificar_banner(banner)
    print(f"Banner: {banner[:45]!r}")
    print(f"  -> Servicio: {r['service']} | Versión: {r['version']} | Riesgo: {r['risk']}\n")
