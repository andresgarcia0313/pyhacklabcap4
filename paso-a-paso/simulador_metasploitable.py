#!/usr/bin/env python3
"""
simulador_metasploitable.py
Simula una máquina Metasploitable 2 (un equipo de práctica con servicios antiguos):
publica en 127.0.0.1 sus banners, en el puerto estándar de cada servicio + 10 000.
Solo escucha en loopback, así que ningún otro equipo puede alcanzarlo.

Uso:  python3 simulador_metasploitable.py                  (normal)
      python3 simulador_metasploitable.py --rechazar-head  (reproduce el Problema 2)
Se detiene con Ctrl+C.
"""
import argparse
import signal
import threading

from servicios_simulados import HOST_SIMULADOR, iniciar


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulador local de Metasploitable 2")
    parser.add_argument("--rechazar-head", action="store_true",
                        help="el servidor web corta las peticiones HEAD (Problema 2)")
    args = parser.parse_args()
    servidores = iniciar(args.rechazar_head)
    puertos = sorted(s.server_address[1] for s in servidores)
    modo = " (HEAD rechazado)" if args.rechazar_head else ""
    print(f"[sim] Metasploitable 2 simulado en {HOST_SIMULADOR}{modo}, puertos {puertos}", flush=True)
    print("[sim] Ctrl+C para detener", flush=True)
    detener = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: detener.set())
    try:
        detener.wait()
    except KeyboardInterrupt:
        pass
    for s in servidores:
        s.server_close()  # los hilos son daemon: terminan con el proceso
    print("[sim] detenido", flush=True)


if __name__ == "__main__":
    main()
