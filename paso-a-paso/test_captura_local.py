"""Pruebas de captura contra servicios simulados en 127.0.0.1 con puertos efímeros (puerto 0)."""
import socket
import unittest

from captura import capturar_banner_tcp, capturar_cabeceras_http
from escaner import escanear_puerto
from servicios_simulados import BANNERS, manejador_apache, manejador_banner, servir

HOST = "127.0.0.1"


def puerto_de(servidor) -> int:
    return servidor.server_address[1]


def puerto_libre() -> int:
    with socket.socket() as s:
        s.bind((HOST, 0))
        return s.getsockname()[1]


class CapturaLocalTest(unittest.TestCase):
    def setUp(self):
        self.servidores = []

    def tearDown(self):
        for s in self.servidores:
            s.shutdown()
            s.server_close()

    def levantar(self, manejador) -> int:
        servidor = servir(manejador, 0, HOST)
        self.servidores.append(servidor)
        return puerto_de(servidor)

    def test_ssh_local_se_clasifica(self):
        r = escanear_puerto(HOST, self.levantar(manejador_banner(BANNERS[22])), "SSH")
        self.assertEqual((r["service"], r["version"]), ("OpenSSH", "4.7p1"))

    def test_puerto_cerrado_se_reporta(self):
        self.assertIn("Puerto cerrado", capturar_banner_tcp(HOST, puerto_libre()))

    def test_sin_banner_da_timeout(self):
        puerto = self.levantar(manejador_banner(b""))
        self.assertIn("Timeout", capturar_banner_tcp(HOST, puerto, timeout=0.5))

    def test_cabeceras_http_locales(self):
        r = capturar_cabeceras_http(HOST, self.levantar(manejador_apache()))
        self.assertEqual(r["status"], 200)
        self.assertIn("Apache/2.2.8", r["banner"])

    def test_http_en_puerto_alto_se_detecta(self):  # se decide por servicio, no por puerto
        r = escanear_puerto(HOST, self.levantar(manejador_apache()), "HTTP-alt")
        self.assertEqual((r["service"], r["http_status"]), ("Apache", 200))

    def test_head_rechazado_usa_get(self):  # Problema 2 del Paso 8
        r = escanear_puerto(HOST, self.levantar(manejador_apache(rechazar_head=True)), "HTTP")
        self.assertEqual((r["service"], r["version"]), ("Apache", "2.2.8"))

    def test_smtp_local(self):  # de extremo a extremo
        r = escanear_puerto(HOST, self.levantar(manejador_banner(BANNERS[25])), "SMTP")
        self.assertEqual(r["service"], "Postfix")

    def test_mysql_handshake_local(self):  # de extremo a extremo
        r = escanear_puerto(HOST, self.levantar(manejador_banner(BANNERS[3306])), "MySQL")
        self.assertEqual((r["service"], r["version"]), ("MySQL", "5.0.51a"))

    def test_https_cerrado_queda_unknown(self):
        r = escanear_puerto(HOST, puerto_libre(), "HTTPS")
        self.assertEqual((r["service"], r["risk"], r["http_status"]), ("N/A", "UNKNOWN", None))


if __name__ == "__main__":
    unittest.main()
