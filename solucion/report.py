"""
report.py - Reporte del escaneo (Paso 5).

Produce dos salidas a partir de la lista de registros del escáner:
  1. Un archivo JSON (JavaScript Object Notation): texto estructurado que otras
     herramientas pueden leer, y que sirve de evidencia para un informe.
     Se parece mucho a un diccionario de Python escrito en un archivo.
  2. Una tabla en consola, para que una persona lea el resultado de un vistazo.

Ojo: los reportes contienen IP, banners y versiones. Trátelos como información
sensible y no los comparta fuera del curso.
"""
import json  # incluido en Python: leer y escribir JSON
import os    # incluido en Python: carpetas y rutas de archivos
from collections import Counter  # incluido en Python: cuenta cuántas veces aparece cada valor
from datetime import datetime, timezone

from config import DIRECTORIO_SALIDA


def generar_reporte_json(resultados: list, host: str,
                         directorio_salida: str = DIRECTORIO_SALIDA) -> str:
    """Guarda los resultados en un archivo JSON y devuelve la ruta del archivo creado."""
    os.makedirs(directorio_salida, exist_ok=True)  # crea la carpeta; si ya existe, no pasa nada
    ahora = datetime.now(timezone.utc)
    # Nombre con fecha y hora hasta el microsegundo, así dos escaneos nunca se sobrescriben.
    # Dentro de { } en un f-string, :%Y%m%d_%H%M%S_%f da formato a la fecha
    # (%Y año, %m mes, %d día, %H hora, %M minutos, %S segundos, %f microsegundos).
    # host.replace('.', '_') cambia los puntos por guiones bajos: 127.0.0.1 -> 127_0_0_1.
    # Ejemplo: banner_report_127_0_0_1_20261020_111326_123456.json
    nombre = f"banner_report_{host.replace('.', '_')}_{ahora:%Y%m%d_%H%M%S_%f}.json"
    ruta = os.path.join(directorio_salida, nombre)  # une carpeta y nombre: output/banner_...
    # Estructura del reporte: un diccionario con otros diccionarios dentro.
    # metadata = quién, cuándo y qué; summary = resumen; results = el detalle por puerto.
    reporte = {
        "metadata": {
            "tool":       "BannerGrabber v1.1 - Laboratorio 4",
            "target":     host,
            "scan_time":  ahora.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "total_ports_scanned": len(resultados),
            "authorization": "Entorno local controlado - simulador de Metasploitable 2",
        },
        # _generar_resumen está definida MÁS ABAJO en este archivo. No hay problema:
        # Python lee primero todo el archivo (con todas sus funciones) y solo ejecuta
        # esta línea cuando alguien llama a generar_reporte_json.
        "summary": _generar_resumen(resultados),
        "results": resultados,
    }
    # open abre (o crea) un archivo; "w" significa "para escribir" (write).
    # "with ... as f" lo cierra solo al terminar el bloque, aunque haya errores.
    with open(ruta, "w", encoding="utf-8") as f:
        # json.dump escribe el diccionario en el archivo con formato JSON.
        # indent=2 lo deja legible; ensure_ascii=False conserva las tildes.
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    return ruta


def _generar_resumen(resultados: list) -> dict:
    """Calcula estadísticas: cuántos servicios hay de cada riesgo y cuáles se identificaron."""
    # r.get("risk", "UNKNOWN") lee la clave "risk" y, si no existe, usa "UNKNOWN".
    # Counter recibe todos esos riesgos y los cuenta: {"CRITICAL": 2, "HIGH": 3, ...}
    conteo_riesgo = Counter(r.get("risk", "UNKNOWN") for r in resultados)
    # Lista "Servicio versión" de lo identificado. Se lee: "para cada r de resultados,
    # arma el texto, solo si su servicio NO es N/A, Unknown ni None".
    servicios_detectados = [
        f"{r.get('service', 'N/A')} {r.get('version', '')}".strip()
        for r in resultados
        if r.get("service") not in ("N/A", "Unknown", None)
    ]
    return {
        "risk_distribution": dict(conteo_riesgo),  # convierte el Counter en un diccionario normal
        "critical_count":    conteo_riesgo.get("CRITICAL", 0),  # 0 si no hay ninguno
        "high_count":        conteo_riesgo.get("HIGH", 0),
        "services_detected": servicios_detectados,
    }


def imprimir_resumen_consola(resultados: list, host: str) -> None:
    """Imprime la tabla de resultados y la distribución de riesgo."""
    print("\n" + "=" * 70)  # el signo + une textos: salto de línea seguido de 70 signos "="
    print(f"  REPORTE DE BANNER GRABBING - Objetivo: {host}")
    print("=" * 70)
    # {'Puerto':<8} escribe el texto "Puerto" y lo rellena con espacios hasta ocupar 8:
    # así se forman las columnas de la tabla.
    print(f"\n{'Puerto':<8} {'Servicio':<14} {'Versión':<25} {'Riesgo':<10} {'Estado HTTP'}")
    print("-" * 70)
    for r in resultados:
        puerto   = str(r.get("port", "?"))      # str() convierte un número en texto
        servicio = r.get("service", "N/A")[:13]  # [:13] recorta para que quepa en la columna
        version  = r.get("version", "N/A")[:24]
        riesgo   = r.get("risk", "UNKNOWN")[:9]
        http_st  = str(r.get("http_status") or "-")  # "-" si no es servicio web (None)
        print(f"{puerto:<8} {servicio:<14} {version:<25} {riesgo:<10} {http_st}")
    resumen = _generar_resumen(resultados)
    print("\n" + "-" * 70)
    print("  DISTRIBUCIÓN DE RIESGO:")
    # .items() entrega pares (nivel, cantidad); sorted los ordena alfabéticamente.
    for nivel, count in sorted(resumen["risk_distribution"].items()):
        print(f"    {nivel:<10}: {'#' * count} ({count})")  # una barra de # por servicio
    # Un número cuenta como verdadero si es distinto de 0: el aviso sale solo si hay alguno.
    if resumen["critical_count"]:
        print(f"\n  [!] ATENCIÓN: {resumen['critical_count']} servicio(s) con riesgo CRÍTICO detectado(s).")
    if resumen["high_count"]:
        print(f"  [!] {resumen['high_count']} servicio(s) con riesgo ALTO detectado(s).")
    print("\n  SERVICIOS IDENTIFICADOS:")
    for svc in resumen["services_detected"]:
        print(f"    - {svc}")
    print("=" * 70 + "\n")
