"""Pruebas de clasificación: cada una comprueba una regla de las firmas de signatures.py."""
import unittest

from servicios_simulados import BANNERS, MYSQL
from signatures import clasificar_banner


def clasificar(banner) -> tuple:
    if isinstance(banner, bytes):
        banner = banner.decode("utf-8", errors="replace").strip()
    r = clasificar_banner(banner)
    return r["service"], r["version"], r["risk"]


class FirmasTest(unittest.TestCase):
    def test_clasificacion_basica(self):
        self.assertEqual(clasificar("SSH-2.0-OpenSSH_4.7p1")[0], "OpenSSH")

    def test_smtp_no_se_confunde_con_ftp(self):  # ambos saludan con 220
        self.assertEqual(clasificar(BANNERS[25]), ("Postfix", "no expuesta", "MEDIUM"))

    def test_postfix_con_version_la_captura(self):  # la versión, no el texto completo
        self.assertEqual(clasificar("220 mail ESMTP Postfix 3.8.6")[1], "3.8.6")

    def test_smtp_generico_no_es_ftp(self):
        self.assertEqual(clasificar("220 mail.example ESMTP Exim 4.97")[0], "SMTP-Generic")

    def test_ftp_generico_sigue_funcionando(self):
        self.assertEqual(clasificar("220 Servidor FTP listo")[0], "FTP-Generic")

    def test_proftpd_conserva_letra_de_version(self):  # 1.3.3c, no 1.3.3
        self.assertEqual(clasificar(BANNERS[21])[1], "1.3.3c")

    def test_mysql_por_handshake_binario(self):
        self.assertEqual(clasificar(MYSQL), ("MySQL", "5.0.51a", "CRITICAL"))

    def test_mysql_en_texto_plano(self):
        self.assertEqual(clasificar("5.0.51a-3ubuntu5 MySQL Server")[0], "MySQL")

    def test_riesgo_depende_de_la_version(self):  # umbral_seguro
        self.assertEqual(clasificar("SSH-2.0-OpenSSH_4.7p1")[2], "HIGH")
        self.assertEqual(clasificar("SSH-2.0-OpenSSH_10.2p1 Ubuntu-2")[2], "LOW")
        self.assertEqual(clasificar("Apache/2.4.51")[2], "LOW")
        self.assertEqual(clasificar("Apache/2.4.50")[2], "HIGH")

    def test_banner_vacio_o_error(self):
        self.assertEqual(clasificar(""), ("N/A", "N/A", "UNKNOWN"))
        self.assertEqual(clasificar("[Timeout - sin respuesta]")[0], "N/A")

    def test_banner_desconocido(self):
        self.assertEqual(clasificar("HOLA 123")[0], "Unknown")


if __name__ == "__main__":
    unittest.main()
