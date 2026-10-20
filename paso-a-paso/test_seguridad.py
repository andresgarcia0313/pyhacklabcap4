"""Pruebas de los controles de uso responsable. Usan mocks: nada sale a la red."""
import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

import banner_grabber
import captura
import config
from report import imprimir_resumen_consola

FUERA_DE_LISTA = "203.0.113.10"  # TEST-NET-3 (RFC 5737): reservada para documentación


class SeguridadTest(unittest.TestCase):
    def test_tcp_fuera_de_lista_no_abre_socket(self):
        with mock.patch.object(captura.socket, "create_connection") as falso:
            with self.assertRaises(PermissionError):
                captura.capturar_banner_tcp(FUERA_DE_LISTA, 22)
        falso.assert_not_called()

    def test_http_fuera_de_lista_no_envia_peticion(self):
        with mock.patch.object(captura.requests, "head") as falso:
            with self.assertRaises(PermissionError):
                captura.capturar_cabeceras_http(FUERA_DE_LISTA, 80)
        falso.assert_not_called()

    def test_main_rechaza_objetivo_no_permitido(self):
        with mock.patch.object(banner_grabber, "TARGET_HOST", FUERA_DE_LISTA), \
             mock.patch.object(banner_grabber, "objetivo_alcanzable") as alcanzable, \
             redirect_stdout(io.StringIO()):
            self.assertEqual(banner_grabber.main(), 2)
        alcanzable.assert_not_called()

    def test_solo_loopback_permitido(self):  # laboratorio 100 % local
        self.assertEqual(config.HOSTS_PERMITIDOS, {"127.0.0.1"})
        self.assertEqual(config.TARGET_HOST, "127.0.0.1")

    def test_no_sigue_redirecciones(self):  # una redirección podría salir de la lista permitida
        respuesta = mock.Mock(status_code=302, headers={"Location": "http://203.0.113.10/"})
        with mock.patch.object(captura.requests, "head", return_value=respuesta) as falso:
            captura.capturar_cabeceras_http("127.0.0.1", 10080)
        self.assertFalse(falso.call_args.kwargs["allow_redirects"])

    def test_columna_http_muestra_guion(self):
        salida = io.StringIO()
        with redirect_stdout(salida):
            imprimir_resumen_consola([{"port": 22, "service": "OpenSSH", "version": "4.7p1",
                                       "risk": "HIGH", "http_status": None}], "127.0.0.1")
        self.assertNotIn("None", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
