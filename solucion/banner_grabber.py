#!/usr/bin/env python3
"""
banner_grabber.py - Programa principal (Paso 6).

(La primera línea, "#!/usr/bin/env python3", le dice a Linux con qué programa
ejecutar este archivo. Para Python es solo un comentario.)

Este archivo no captura ni clasifica nada por sí mismo: ORQUESTA a los demás.
Flujo:
  1. Verifica que el objetivo esté en la lista permitida  (config.py)
  2. Comprueba que el objetivo responda                    (este archivo)
  3. Escanea todos los puertos en paralelo                 (escaner.py)
  4. Muestra el resumen en consola                         (report.py)
  5. Guarda el reporte JSON en output/                     (report.py)

Uso exclusivo sobre entornos autorizados: aquí, el simulador local en 127.0.0.1.
Ejecútelo con:  python3 banner_grabber.py
"""
import socket

from config import MAX_WORKERS, TARGET_HOST, TARGET_PORTS, verificar_host
from escaner import ejecutar_escaneo
from report import generar_reporte_json, imprimir_resumen_consola


def objetivo_alcanzable(host: str, puertos: dict) -> bool:
    """
    Comprueba que al menos UN puerto del objetivo acepte conexiones.
    Si ninguno responde, no tiene sentido escanear (por ejemplo, el simulador está apagado).
    Devuelve True (verdadero) o False (falso): eso indica "-> bool".
    """
    for puerto in puertos:  # recorrer un diccionario recorre sus claves: los números de puerto
        try:
            with socket.create_connection((host, puerto), timeout=2):
                return True  # la conexión funcionó: el objetivo está vivo (return sale de la función)
        except OSError:
            continue  # ese puerto no respondió: probar el siguiente
    return False  # se probaron todos y ninguno respondió


def imprimir_encabezado() -> None:
    """Imprime el recuadro de presentación."""
    print("+" + "-" * 62 + "+")
    # .ljust(63) rellena el texto con espacios a la derecha hasta 63 caracteres,
    # para que el borde "|" quede alineado.
    print("|  BANNER GRABBER - Laboratorio 4 (Uso Educativo)".ljust(63) + "|")
    print("|  Ejecutar SOLO sobre sistemas con autorización escrita".ljust(63) + "|")
    print("+" + "-" * 62 + "+")


def main() -> int:
    """
    Ejecuta el escaneo completo y devuelve un CÓDIGO DE SALIDA (un número entero)
    que otros programas pueden leer para saber qué pasó:
    0 = todo bien, 1 = el objetivo no responde, 2 = destino no permitido.
    En la terminal se consulta, justo después de ejecutar, con: echo $?
    """
    imprimir_encabezado()
    print(f"\n[*] Objetivo: {TARGET_HOST}")
    print(f"[*] Puertos a escanear: {list(TARGET_PORTS)}")  # list(diccionario) = lista de sus claves
    # 1. Lista permitida, ANTES de cualquier conexión.
    try:
        verificar_host(TARGET_HOST)
    except PermissionError as e:  # el error que lanza verificar_host (config.py)
        print(f"[!] {e}")
        return 2
    # 2. ¿Responde el objetivo?
    print("\n[*] Verificando conectividad con el objetivo...")
    if not objetivo_alcanzable(TARGET_HOST, TARGET_PORTS):
        print(f"[!] Ningún puerto responde en {TARGET_HOST}. Inicie el simulador en otra terminal:")
        print("    python3 simulador_metasploitable.py")
        return 1
    print(f"[+] Objetivo {TARGET_HOST} alcanzable.")
    print("[!] Los reportes contienen IP, banners y versiones: trátelos como datos sensibles.")
    # 3, 4 y 5. Escanear, resumir y guardar.
    resultados = ejecutar_escaneo(TARGET_HOST, TARGET_PORTS, MAX_WORKERS)
    imprimir_resumen_consola(resultados, TARGET_HOST)
    # Dentro de { } también se puede llamar una función: aquí se guarda el JSON
    # y se imprime la ruta que devuelve.
    print(f"[+] Reporte guardado en: {generar_reporte_json(resultados, TARGET_HOST)}")
    print("[*] Escaneo completado.\n")
    return 0


# Este bloque solo se ejecuta cuando el archivo se corre directamente
# (python3 banner_grabber.py), y NO cuando otro archivo lo importa.
# __name__ es una variable que Python crea solo: vale "__main__" en el archivo
# que se ejecutó desde la terminal.
# raise SystemExit(...) termina el programa y entrega al sistema el código de main().
if __name__ == "__main__":
    raise SystemExit(main())
