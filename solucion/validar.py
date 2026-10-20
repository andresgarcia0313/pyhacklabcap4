#!/usr/bin/env python3
"""
validar.py
Sección 7 de la guía, con comprobaciones que SÍ pueden fallar:
  7.1 el reporte JSON existe, es válido y tiene los conteos esperados.
  7.2 la clasificación de banners acierta en casos conocidos.
  7.3 cada puerto abierto dejó un banner crudo en el reporte.
Uso: python3 validar.py   (después de ejecutar banner_grabber.py)
Sale con código 0 si todo pasa y 1 si algo falla.
"""
import glob
import json
import os
import sys

from config import TARGET_HOST
from servicios_simulados import MYSQL
from signatures import clasificar_banner

fallos = []


def comprobar(nombre: str, obtenido, esperado) -> None:
    ok = obtenido == esperado
    print(f"  {'PASS' if ok else 'FAIL'} | {nombre}: obtenido={obtenido!r} esperado={esperado!r}")
    if not ok:
        fallos.append(nombre)


def ultimo_reporte() -> dict:
    archivos = glob.glob("output/banner_report_*.json")
    if not archivos:
        sys.exit("FAIL | No hay reportes en output/. Ejecute primero: python3 banner_grabber.py")
    ultimo = max(archivos, key=os.path.getmtime)
    with open(ultimo, encoding="utf-8") as f:
        reporte = json.load(f)  # si el JSON no es válido, aquí se detiene con el error
    print(f"  JSON válido: {ultimo}")
    return reporte


def validar_71(reporte: dict) -> None:
    print("\n7.1 Reporte JSON")
    comprobar("Puertos escaneados", reporte["metadata"]["total_ports_scanned"], 7)
    comprobar("Objetivo", reporte["metadata"]["target"], TARGET_HOST)
    comprobar("Servicios CRITICAL", reporte["summary"]["critical_count"], 2)
    comprobar("Servicios HIGH", reporte["summary"]["high_count"], 3)


def validar_72() -> None:
    print("\n7.2 Clasificación de banners")
    casos = [
        ("220 ProFTPD 1.3.3c Server",                    ("ProFTPD", "1.3.3c", "CRITICAL")),
        ("220 (vsFTPd 2.3.4)",                           ("vsftpd", "2.3.4", "CRITICAL")),
        ("SSH-2.0-OpenSSH_4.7p1 Debian",                 ("OpenSSH", "4.7p1", "HIGH")),
        ("SSH-2.0-OpenSSH_10.2p1 Ubuntu",                ("OpenSSH", "10.2p1", "LOW")),
        ("220 metasploitable.localdomain ESMTP Postfix (Ubuntu)", ("Postfix", "no expuesta", "MEDIUM")),
        ("Apache/2.2.8 (Ubuntu) DAV/2 | PHP/5.2.4",      ("Apache", "2.2.8", "HIGH")),
        ("Apache/2.4.62 (Debian)",                       ("Apache", "2.4.62", "LOW")),
        (MYSQL.decode("utf-8", errors="replace"),        ("MySQL", "5.0.51a", "CRITICAL")),
        ("",                                             ("N/A", "N/A", "UNKNOWN")),
    ]
    for banner, esperado in casos:
        r = clasificar_banner(banner)
        comprobar(ascii(banner[:30]), (r["service"], r["version"], r["risk"]), esperado)


def validar_73(reporte: dict) -> None:
    print("\n7.3 Banners crudos (ascii() muestra los bytes de control sin romper la línea)")
    abiertos = [r for r in reporte["results"] if r.get("banner_raw") and not r["banner_raw"].startswith("[")]
    for r in abiertos:
        print(f"    Puerto {r['port']:>5}: {ascii(r['banner_raw'][:70])}")
    comprobar("Puertos con banner", len(abiertos), 6)


if __name__ == "__main__":
    reporte = ultimo_reporte()
    validar_71(reporte)
    validar_72()
    validar_73(reporte)
    print(f"\nResultado final: {'TODO PASA' if not fallos else f'{len(fallos)} FALLO(S): {fallos}'}")
    sys.exit(1 if fallos else 0)
