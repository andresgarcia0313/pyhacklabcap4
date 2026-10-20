"""
servicios_simulados.py
Servicios falsos que imitan a Metasploitable 2. Cada uno solo envía su banner:
no hay FTP, SSH ni MySQL reales detrás, así que no hay nada vulnerable expuesto.

Concepto: muchos servicios se presentan solos al aceptar la conexión
(FTP, SSH, SMTP y MySQL); los servidores web, en cambio, esperan una petición.
"""
import http.server
import socketserver
import threading

from config import DESPLAZAMIENTO

HOST_SIMULADOR = "127.0.0.1"  # solo loopback: ningún otro equipo puede alcanzarlo

APACHE = {"Server": "Apache/2.2.8 (Ubuntu) DAV/2", "X-Powered-By": "PHP/5.2.4-2ubuntu5.10"}
# Handshake MySQL: longitud (3 bytes), secuencia, protocolo 10 (0x0a),
# versión terminada en NUL y datos de sesión. Es binario, no texto.
MYSQL = b"\x21\x00\x00\x00\x0a5.0.51a-3ubuntu5\x00\x08\x00\x00\x00abcdefgh\x00\x2c\xa2"
BANNERS = {
    21:   b"220 ProFTPD 1.3.3c Server (ProFTPD Default Installation) [127.0.0.1]\r\n",
    22:   b"SSH-2.0-OpenSSH_4.7p1 Debian-8ubuntu1\r\n",
    25:   b"220 metasploitable.localdomain ESMTP Postfix (Ubuntu)\r\n",
    3306: MYSQL,
}
PUERTOS_WEB = (80, 8080)  # el 443 queda cerrado a propósito, para ver cómo se reporta un puerto cerrado


class _Servidor(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class _ServidorWeb(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def manejador_banner(banner: bytes):
    """Servicio que saluda con su banner (o calla si es b'') y espera a que el cliente cierre."""
    class Manejador(socketserver.BaseRequestHandler):
        def handle(self):
            if banner:
                self.request.sendall(banner)
            self.request.settimeout(10)
            try:
                self.request.recv(1)
            except OSError:
                pass
    return Manejador


def manejador_apache(rechazar_head: bool = False, cabeceras: dict = APACHE):
    """Servidor web con cabeceras de Apache 2.2.8; con rechazar_head corta los HEAD (Problema 2)."""
    class Apache(http.server.BaseHTTPRequestHandler):
        def version_string(self):  # send_response la usa para la cabecera Server
            return cabeceras["Server"]

        def do_GET(self):
            self.send_response(200)
            for nombre, valor in cabeceras.items():
                if nombre != "Server":
                    self.send_header(nombre, valor)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_HEAD(self):
            if rechazar_head:
                self.close_connection = True  # cierra sin responder: RemoteDisconnected
                return
            self.do_GET()

        def log_message(self, format, *args):  # sin registro de peticiones en consola
            pass
    return Apache


def servir(manejador, puerto: int, host: str = HOST_SIMULADOR):
    """Arranca un servidor en un hilo; con puerto 0 el sistema elige uno libre."""
    web = issubclass(manejador, http.server.BaseHTTPRequestHandler)
    servidor = (_ServidorWeb if web else _Servidor)((host, puerto), manejador)
    threading.Thread(target=servidor.serve_forever, daemon=True).start()
    return servidor


def iniciar(rechazar_head: bool = False) -> list:
    """Levanta todos los servicios simulados en su puerto estándar + DESPLAZAMIENTO."""
    servidores = [servir(manejador_banner(b), p + DESPLAZAMIENTO) for p, b in BANNERS.items()]
    servidores += [servir(manejador_apache(rechazar_head), p + DESPLAZAMIENTO) for p in PUERTOS_WEB]
    return servidores
