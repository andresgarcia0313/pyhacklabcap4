"""
config.py - Configuración central de la herramienta (Paso 1).

Este texto entre tres comillas dobles es un DOCSTRING: una nota que describe el
archivo. Python no la ejecuta; está ahí para las personas que leen el código.

Qué hace este archivo: guarda en un solo lugar todos los valores que podrían
cambiar (a quién se escanea, qué puertos, cuánto se espera, qué destinos están
permitidos). Los demás archivos toman estos valores de aquí.

Glosario de redes:
  - Host: el equipo al que nos conectamos. "127.0.0.1" (también llamado
    "localhost" o "loopback") es SU PROPIO computador: el tráfico nunca sale de él.
  - Puerto: número de 0 a 65535 que identifica a un servicio dentro de un equipo.
    Por ejemplo, SSH suele usar el 22 y la web el 80.
  - Servicio: programa que escucha en un puerto y responde (FTP, SSH, un servidor web...).
"""

# Las líneas que empiezan con # son COMENTARIOS: Python las ignora por completo.
# Sirven para explicar el código. En este laboratorio hay muchos: léalos todos.

# ---------------------------------------------------------------------------
# OBJETIVO DEL ESCANEO
# ---------------------------------------------------------------------------
# Una VARIABLE es un nombre que guarda un valor. El signo = significa "guardar":
# a la izquierda va el nombre y a la derecha el valor.
# Lo que va entre comillas es un TEXTO (en Python se llama "string" o str).
# Por costumbre, los valores que no cambian se escriben en MAYÚSCULAS.
TARGET_HOST = "127.0.0.1"  # el simulador de Metasploitable 2, en su propio equipo

# Las llaves { } con valores sueltos forman un CONJUNTO (set): una colección sin
# repetidos donde se puede preguntar rápidamente "¿este valor está aquí?".
# Esta es la LISTA PERMITIDA: los únicos destinos que la herramienta puede escanear.
# Escanear equipos sin autorización escrita es ilegal en muchos países:
# agregue otra IP solo con autorización del instructor.
HOSTS_PERMITIDOS = {"127.0.0.1"}

# ---------------------------------------------------------------------------
# PUERTOS A ESCANEAR
# ---------------------------------------------------------------------------
# Un número sin comillas es un ENTERO (int). Con él se puede hacer aritmética.
# Cada servicio tiene un PUERTO ESTÁNDAR, el que usa por costumbre: FTP el 21,
# SSH el 22, la web el 80. Pero los puertos por debajo de 1024 necesitan permisos
# de administrador, y el 22 ya puede estar ocupado por el SSH real de su equipo.
# Por eso el simulador usa el puerto estándar + 10 000 (el 21 pasa a 10021, el 3306 a 13306).
DESPLAZAMIENTO = 10000

# Las llaves con pares "clave: valor" forman un DICCIONARIO (dict): una tabla
# que asocia cada clave con su valor. Aquí, cada puerto estándar con el nombre de su servicio.
# Se lee así: PUERTOS_ESTANDAR[22] devuelve "SSH".
# Los elementos se separan con comas; los espacios extra solo alinean el texto.
PUERTOS_ESTANDAR = {
    21:   "FTP",       # transferencia de archivos
    22:   "SSH",       # consola remota cifrada
    25:   "SMTP",      # envío de correo
    80:   "HTTP",      # servidor web
    443:  "HTTPS",     # servidor web cifrado (en el simulador queda cerrado a propósito)
    3306: "MySQL",     # base de datos
    8080: "HTTP-alt",  # servidor web en un puerto alterno
}

# Esta línea arma un diccionario nuevo a partir de otro (se llama "comprensión
# de diccionario"). Léala de derecha a izquierda:
#   for puerto, servicio in PUERTOS_ESTANDAR.items()  -> recorre cada par (21, "FTP"), (22, "SSH")...
#   puerto + DESPLAZAMIENTO: servicio             -> y guarda 10021: "FTP", 10022: "SSH"...
# Resultado: {10021: "FTP", 10022: "SSH", ..., 18080: "HTTP-alt"}
TARGET_PORTS = {puerto + DESPLAZAMIENTO: servicio for puerto, servicio in PUERTOS_ESTANDAR.items()}

# Servicios web: a estos hay que "preguntarles" con una petición HTTP para que respondan.
# Se decide por el NOMBRE del servicio y no por el número de puerto, así funciona
# aunque el servidor web esté en un puerto poco común (como el 10080).
SERVICIOS_HTTP = {"HTTP", "HTTPS", "HTTP-alt"}

# ---------------------------------------------------------------------------
# PARÁMETROS DE CONEXIÓN
# ---------------------------------------------------------------------------
# Un número con punto decimal es un FLOTANTE (float): 4.0 significa cuatro segundos.
SOCKET_TIMEOUT   = 4.0   # segundos máximos esperando un banner antes de rendirse
HTTP_TIMEOUT     = 5.0   # segundos máximos esperando una respuesta web
MAX_BANNER_BYTES = 2048  # bytes máximos a leer de cada banner (suficiente para identificarlo)
MAX_WORKERS      = 4     # cuántos puertos se revisan al mismo tiempo (hilos en paralelo)
DIRECTORIO_SALIDA = "output"  # carpeta donde se guardan los reportes JSON

# ---------------------------------------------------------------------------
# NIVELES DE RIESGO
# ---------------------------------------------------------------------------
# Otro diccionario: cada nivel de riesgo (clave) con su significado (valor).
# CVE significa "Common Vulnerabilities and Exposures": el identificador público
# de una vulnerabilidad, por ejemplo CVE-2024-6387.
RISK_LEVELS = {
    "CRITICAL": "Versión con vulnerabilidades críticas conocidas (CVE publicados)",
    "HIGH":     "Versión desactualizada con vulnerabilidades de alto impacto",
    "MEDIUM":   "Versión con posibles vulnerabilidades o configuración débil",
    "LOW":      "Versión igual o posterior al umbral seguro definido en la firma",
    "INFO":     "Servicio detectado pero sin clasificación de riesgo disponible",
    "UNKNOWN":  "No se pudo identificar la versión del servicio",
}


# ---------------------------------------------------------------------------
# CONTROL DE USO RESPONSABLE
# ---------------------------------------------------------------------------
# "def" define una FUNCIÓN: un bloque de código con nombre que se ejecuta cada
# vez que alguien la "llama" escribiendo verificar_host("127.0.0.1").
#   - (host: str) es el PARÁMETRO: el dato que recibe. ": str" indica que se
#     espera un texto (es solo una pista para quien lee; Python no lo exige).
#   - "-> None" indica que la función no devuelve ningún resultado.
#   - Los dos puntos ":" abren el bloque, y todo lo que está SANGRADO (movido
#     4 espacios a la derecha) pertenece a la función. En Python la sangría
#     no es decoración: define qué líneas van dentro de qué bloque.
def verificar_host(host: str) -> None:
    """Detiene el programa si el destino no está en la lista permitida."""
    # "if" ejecuta el bloque de abajo solo si la condición es verdadera.
    # "not in" pregunta "¿el host NO está en el conjunto?".
    if host not in HOSTS_PERMITIDOS:
        # "raise" lanza un ERROR (excepción) que interrumpe todo lo que se estaba
        # haciendo, ANTES de que se abra cualquier conexión.
        # La f antes de las comillas crea un "f-string": lo que va entre { } se
        # reemplaza por su valor. Si host vale "203.0.113.10", el mensaje dirá
        # "Host 203.0.113.10 fuera de la lista permitida del laboratorio".
        raise PermissionError(f"Host {host} fuera de la lista permitida del laboratorio")
