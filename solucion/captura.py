"""
captura.py - Captura de banners (Paso 3).

"Banner grabbing" es conectarse a un puerto y leer lo que el servicio dice de sí
mismo: producto y versión. Hay dos tipos de servicio:
  1. Los que HABLAN PRIMERO (FTP, SSH, SMTP, MySQL): al conectarnos envían su
     saludo sin que les preguntemos. Basta con conectarse y leer.
  2. Los que ESPERAN UNA PREGUNTA (servidores web): no dicen nada hasta recibir
     una petición HTTP. Se les envía HEAD ("dame solo las cabeceras") y se leen
     las cabeceras "Server" y "X-Powered-By", que revelan el software.

Es "fingerprinting activo": enviamos tráfico al objetivo. Es preciso, pero el
objetivo puede notarlo, y por eso exige autorización.
"""
# "import X" trae un módulo completo; luego se usa como X.algo (socket.create_connection).
import socket    # incluido en Python: conexiones de red de bajo nivel

import requests  # librería EXTERNA para peticiones HTTP (se instaló con pip en el Paso 0)
import urllib3   # librería que usa requests por debajo; la usamos para silenciar un aviso

# "from X import Y" trae solo los nombres indicados, que luego se usan directamente
# (RequestException en lugar de requests.exceptions.RequestException).
from requests.exceptions import RequestException  # error general de requests

# También se puede importar de los archivos propios: estos valores vienen de config.py
# (Paso 1). Por eso todos los archivos deben estar en la misma carpeta.
from config import HTTP_TIMEOUT, MAX_BANNER_BYTES, SOCKET_TIMEOUT, verificar_host

# Más abajo usamos verify=False (aceptar certificados no verificados). requests
# avisaría en cada petición; aquí silenciamos ese aviso. Solo es aceptable porque
# verificar_host limita los destinos al laboratorio.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Lista de cabeceras HTTP que delatan el software del servidor web.
CABECERAS_INTERES = ["Server", "X-Powered-By", "X-Generator",
                     "X-AspNet-Version", "X-Runtime", "Via", "Set-Cookie"]
# Nos identificamos con honestidad ante el servidor (cabecera User-Agent).
USER_AGENT = {"User-Agent": "BannerGrabber/1.0 (Lab04 Educational)"}


def sonda_http(host: str) -> bytes:
    r"""
    Petición HTTP mínima, escrita a mano, para enviarla por un socket.
    b"..." es un texto en BYTES: por la red viajan bytes, no textos de Python.
    \r\n es el salto de línea que exige HTTP; una línea vacía al final cierra la petición.
    """
    # host.encode() convierte el texto en bytes; el signo + une los pedazos de bytes.
    return b"HEAD / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n"


# "sonda: bytes | None = None" significa: puede recibir bytes o nada (None), y si
# quien llama no la indica, vale None.
def capturar_banner_tcp(host: str, puerto: int, timeout: float = SOCKET_TIMEOUT,
                        sonda: bytes | None = None) -> str:
    """
    Se conecta por TCP a host:puerto y lee el banner de bienvenida.
    Si se pasa una "sonda" (una petición), la envía antes de leer.
    Devuelve el banner como texto, o un mensaje de error entre corchetes.
    """
    verificar_host(host)  # control de uso responsable: ANTES de abrir cualquier conexión
    # "try" intenta ejecutar el bloque. Si ocurre un error, Python salta al "except"
    # que corresponde a ese tipo de error, en lugar de detener el programa.
    try:
        # create_connection abre la conexión TCP (el "saludo de tres vías" de la red).
        # (host, puerto) entre paréntesis es una tupla: la dirección completa.
        # "with ... as s" guarda la conexión en la variable s y garantiza que se
        # cierre al terminar el bloque, pase lo que pase.
        with socket.create_connection((host, puerto), timeout=timeout) as s:
            if sonda:
                s.sendall(sonda)  # envía la petición completa
            # recv espera datos del servicio; si no llegan en "timeout" segundos, falla.
            datos = s.recv(MAX_BANNER_BYTES)
            # decode convierte bytes en texto con la codificación UTF-8. Si algún byte no
            # es UTF-8 válido, errors="replace" lo cambia por el símbolo � en lugar de fallar.
            # Los bytes de control válidos (como el byte nulo \x00 del saludo de MySQL) se
            # conservan, y por eso la firma de MySQL puede buscarlos.
            # strip quita espacios y saltos de línea de los extremos.
            return datos.decode("utf-8", errors="replace").strip()
    # Cada tipo de fallo se devuelve como texto entre corchetes, sin detener el programa:
    except socket.timeout:          # no hubo respuesta a tiempo, al conectar o al leer
        return "[Timeout - sin respuesta]"
    except ConnectionRefusedError:  # nadie escucha en ese puerto: está cerrado
        return "[Puerto cerrado - conexión rechazada]"
    except OSError as e:            # cualquier otro problema de red; "as e" guarda el error en e
        return f"[Error de red: {e}]"


def _pedir(url: str, timeout: float) -> requests.Response:
    """
    Pide las cabeceras al servidor web. Primero con HEAD; si el servidor lo rechaza
    (código 405 o 501) o corta la conexión, reintenta con GET.
    """
    # verify=False: acepta certificados autofirmados (comunes en laboratorios).
    # allow_redirects=False: no seguir redirecciones; interesan las cabeceras de ESTE
    # servidor, y una redirección podría llevar la petición a un equipo no autorizado.
    # True y False son los valores lógicos verdadero y falso (tipo bool).
    opciones = {"timeout": timeout, "verify": False, "allow_redirects": False, "headers": USER_AGENT}
    try:
        # **opciones "desempaca" el diccionario: equivale a escribir
        # requests.head(url, timeout=..., verify=False, allow_redirects=False, headers=...)
        respuesta = requests.head(url, **opciones)
        # respuesta.status_code es el código HTTP: 200 = OK, 405 = método no permitido...
        # "not in (405, 501)" pregunta si NO es ninguno de esos dos.
        if respuesta.status_code not in (405, 501):
            return respuesta
    except requests.exceptions.SSLError:
        raise  # un error de certificado no se arregla con GET: se deja pasar hacia arriba
    except RequestException:
        pass   # "pass" no hace nada: el servidor cortó ante HEAD y probaremos con GET
    # stream=True: recibe las cabeceras sin descargar la página; close() corta lo demás.
    respuesta = requests.get(url, stream=True, **opciones)
    respuesta.close()
    return respuesta


def capturar_cabeceras_http(host: str, puerto: int, timeout: float = HTTP_TIMEOUT,
                            tls: bool = False) -> dict:
    """
    Consulta un servidor web y arma un "banner" uniendo las cabeceras Server y
    X-Powered-By, para clasificarlo igual que un banner TCP.
    tls=True usa https (HTTP cifrado con TLS, Transport Layer Security).
    """
    verificar_host(host)  # control de uso responsable: ANTES de la petición
    # "A if condición else B" elige A si la condición es verdadera, o B si no.
    # Resultado, por ejemplo: "http://127.0.0.1:10080/"
    url = f"{'https' if tls else 'http'}://{host}:{puerto}/"
    resultado = {"url": url, "status": None, "headers": {}, "banner": ""}
    try:
        respuesta = _pedir(url, timeout)
    except requests.exceptions.SSLError:
        resultado["banner"] = "[SSL Error - certificado inválido]"  # cambia el valor de "banner"
        return resultado
    except RequestException as e:  # puerto cerrado, sin respuesta, conexión cortada...
        resultado["banner"] = f"[HTTP Error: {e}]"
        return resultado
    resultado["status"] = respuesta.status_code  # por ejemplo 200 = "OK"
    for cabecera in CABECERAS_INTERES:
        valor = respuesta.headers.get(cabecera)  # .get devuelve None si la cabecera no existe
        if valor:  # un valor vacío o None cuenta como falso: solo se guardan las que existen
            resultado["headers"][cabecera] = valor
    # Lista con Server y X-Powered-By, solo las que existan (se lee: "para cada c de
    # esas dos, toma su valor, si c está en las cabeceras").
    partes = [resultado["headers"][c] for c in ("Server", "X-Powered-By") if c in resultado["headers"]]
    # " | ".join(partes) une los elementos de la lista con " | " entre ellos.
    # La barra \ al final de la línea indica que la instrucción sigue en la línea siguiente.
    resultado["banner"] = " | ".join(partes) if partes \
        else f"HTTP {respuesta.status_code} (sin cabecera Server)"
    return resultado
