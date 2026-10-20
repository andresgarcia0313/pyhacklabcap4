r"""
signatures.py - Diccionario de firmas y clasificación de banners (Paso 2).

Un BANNER es el texto con el que un servicio se presenta, por ejemplo:
    "SSH-2.0-OpenSSH_4.7p1 Debian-8ubuntu1"
Una FIRMA es una EXPRESIÓN REGULAR (regex): un patrón para buscar texto.
Cada firma reconoce un producto dentro del banner y extrae su versión.

Cómo leer un patrón, con el ejemplo r"ProFTPD\s+([\d\.]+[a-z]?)":
    ProFTPD    el texto literal "ProFTPD"
    \s+        uno o más espacios en blanco (\s = espacio, tabulación o salto de
               línea; + = "uno o más" de lo que va justo antes)
    ( ... )    GRUPO DE CAPTURA: la parte que queremos guardar (la versión)
    [\d\.]+    uno o más dígitos (\d) o puntos (\.), como "1.3.3"
    [a-z]?     una letra opcional al final (? = "puede estar o no"), como la "c" de "1.3.3c"

Otros símbolos que aparecen en las firmas de este archivo:
    [ ... ]    UNO de los caracteres de adentro: [- ] es un guion o un espacio;
               [a-z] es cualquier letra minúscula
    [^ ... ]   cualquier carácter EXCEPTO los de adentro: [^\x00] = cualquiera menos el byte nulo
    *          "cero o más" de lo que va justo antes (+ exige al menos uno)
    {0,80}     "entre 0 y 80" de lo que va justo antes
    .          cualquier carácter, excepto el salto de línea
    \w         una letra, un dígito o un guion bajo
    [\s\S]     cualquier carácter, incluido el salto de línea (espacio o no espacio)
    \x00       el byte con valor 0 (\x seguido de dos cifras hexadecimales = un byte)
    \b         un borde de palabra: donde empieza o termina una palabra
    ^          "al inicio de la línea"
    (?: ... )  agrupa sin capturar: sirve para aplicar ? a varias piezas a la vez

IMPORTANTE: gana la PRIMERA firma que coincide. Por eso las específicas van antes
que las genéricas (por ejemplo, las de correo SMTP antes que la genérica de FTP).

(La r antes de las comillas de este docstring evita que Python interprete las
barras \ del texto; más abajo se explica con detalle.)
"""
# "import" trae código que otras personas ya escribieron. "re" es el MÓDULO
# (archivo de código) de Python para expresiones regulares; viene incluido.
# Después de importarlo se usan sus funciones así: re.search(...), re.findall(...).
import re


# Una función puede recibir varios parámetros, separados por comas.
# "version_group=1" da un VALOR POR DEFECTO: si quien llama no lo indica, vale 1.
# "None" es el valor especial de Python que significa "nada" o "no hay".
def _firma(service, pattern, risk, note, version_group=1, umbral_seguro=None):
    """
    Arma una firma como diccionario (es solo un atajo para no repetir las claves).
      service:       nombre legible del producto
      pattern:       expresión regular que lo reconoce
      risk:          nivel de riesgo si la versión es vieja (ver RISK_LEVELS en config.py)
      note:          explicación breve del riesgo
      version_group: qué grupo de captura contiene la versión (0 = todo el texto encontrado)
      umbral_seguro: versión desde la cual el riesgo baja a LOW; None = el riesgo no cambia
    """
    # "return" entrega el resultado a quien llamó la función y la termina.
    # El guion bajo inicial en _firma es una convención: "uso interno de este archivo".
    return {"service": service, "pattern": pattern, "risk": risk, "note": note,
            "version_group": version_group, "umbral_seguro": umbral_seguro}


# Los corchetes [ ] forman una LISTA: una colección ORDENADA de elementos.
# Aquí cada elemento es una firma creada con _firma(...). Python permite partir
# una instrucción en varias líneas mientras haya un paréntesis o corchete abierto.
#
# La r antes de las comillas crea un "raw string" (texto crudo): Python no interpreta
# las barras invertidas \, así llegan intactas al motor de expresiones regulares.
# Sin la r, Python intentaría entender "\d" o "\s" por su cuenta.
SIGNATURES = [
    # -- FTP (transferencia de archivos) --------------------------------
    _firma("ProFTPD", r"ProFTPD\s+([\d\.]+[a-z]?)", "CRITICAL",
           "ProFTPD 1.3.3c: el código fuente distribuido en 2010 traía una puerta trasera"),
    _firma("vsftpd", r"vsftpd\s+([\d\.]+)", "CRITICAL",
           "vsftpd 2.3.4 presente en Metasploitable 2 - backdoor conocido en puerto 6200"),
    # -- SMTP (correo). Va ANTES que FTP-Generic: ambos saludan con el código 220 --
    # (?:[ /]([\d\.]+))? significa "y, si existe, una versión": por eso puede no haberla.
    _firma("Postfix", r"^220[- ].*Postfix(?:[ /]([\d\.]+))?", "MEDIUM",
           "Servidor Postfix; verificar configuración de relay abierto"),
    _firma("Sendmail", r"^220[- ].*Sendmail\s+([\d\.]+)", "HIGH",
           "Sendmail con versión expuesta; historial de vulnerabilidades conocido"),
    # \bE?SMTP\b busca la palabra SMTP o ESMTP completa (\b = borde de palabra).
    _firma("SMTP-Generic", r"^220[- ](.{0,80}\bE?SMTP\b.*)", "INFO",
           "Servidor SMTP genérico detectado"),
    # Cualquier otro saludo "220 ..." se asume FTP: .{1,60} toma de 1 a 60 caracteres.
    _firma("FTP-Generic", r"^220[- ](.{1,60})", "INFO",
           "Servidor FTP genérico; versión no identificada por firma específica"),
    # -- SSH (consola remota cifrada) ------------------------------------
    # Aquí se indica umbral_seguro por su NOMBRE (umbral_seguro="9.8"): así no hace
    # falta escribir antes todos los parámetros que tienen valor por defecto.
    _firma("OpenSSH", r"SSH-[\d\.]+-OpenSSH_([\d\.p]+)", "HIGH",
           "OpenSSH anterior al umbral 9.8p1 (la que corrige CVE-2024-6387); revise los CVE de esta versión",
           umbral_seguro="9.8"),
    _firma("SSH-Generic", r"^SSH-([\d\.]+)-(.+)", "INFO",
           "Implementación SSH no identificada por firma específica", version_group=2),
    # -- Servidores web (vienen de la cabecera HTTP "Server") -------------
    _firma("Apache", r"Apache/([\d\.]+)", "HIGH",
           "Apache anterior al umbral 2.4.51 (la que corrige CVE-2021-42013); revise los CVE de esta versión",
           umbral_seguro="2.4.51"),
    _firma("Nginx", r"nginx/([\d\.]+)", "MEDIUM", "Nginx con versión expuesta en cabecera Server"),
    _firma("IIS", r"Microsoft-IIS/([\d\.]+)", "MEDIUM", "Microsoft IIS con versión expuesta"),
    _firma("PHP", r"PHP/([\d\.]+)", "HIGH",
           "PHP expuesto en X-Powered-By; ramas sin soporte con múltiples CVE", umbral_seguro="8.2"),
    # -- MySQL (base de datos). Puede llegar como texto o como saludo BINARIO --
    _firma("MySQL", r"(\d+\.\d+\.\d+[a-z]?)-[^\x00]*MySQL", "CRITICAL",
           "MySQL expuesto; en Metasploitable 2 acepta root sin contraseña"),
    # Saludo binario: hasta 4 bytes de cabecera, el byte 0x0a (protocolo 10),
    # la versión y un byte nulo \x00 que marca el fin del texto.
    _firma("MySQL", r"^[\s\S]{0,4}\x0a(\d+\.\d+\.\d+[a-z]?)[\w\.-]*\x00", "CRITICAL",
           "MySQL detectado por handshake binario; en Metasploitable 2 acepta root sin contraseña"),
    # -- Comodín final: .+ coincide con cualquier texto no vacío -----------
    _firma("Unknown", r".+", "UNKNOWN",
           "Banner capturado pero no coincide con ninguna firma conocida", version_group=0),
]

# Resultado cuando no hay banner que clasificar (puerto cerrado, sin respuesta...).
SIN_BANNER = {"service": "N/A", "version": "N/A", "risk": "UNKNOWN",
              "note": "No se pudo capturar el banner o el puerto está cerrado"}


def _como_tupla(version: str) -> tuple:
    """
    Convierte una versión en números para poder compararla: "4.7p1" -> (4, 7, 1).
    Comparadas como texto, "10.2" quedaría ANTES que "9.8" (porque "1" < "9");
    como números, (10, 2) > (9, 8), que es lo correcto.
    """
    # re.findall(r"\d+", "4.7p1") devuelve la lista de grupos de dígitos: ["4", "7", "1"].
    # int(n) convierte cada texto en número: "4" -> 4.
    # tuple(... for n in ...) recorre la lista, convierte cada elemento y arma una
    # TUPLA: como una lista, pero que no se puede modificar. Las tuplas se comparan
    # elemento por elemento, igual que se comparan versiones.
    return tuple(int(n) for n in re.findall(r"\d+", version))


def _riesgo(firma: dict, version: str) -> tuple:
    """Devuelve (riesgo, nota). Si la versión alcanza el umbral seguro, el riesgo baja a LOW."""
    # firma["umbral_seguro"] lee del diccionario el valor guardado con esa clave.
    umbral = firma["umbral_seguro"]
    # "and" exige que ambas condiciones sean verdaderas. Un valor None cuenta como
    # falso, así que si la firma no tiene umbral, la comparación ni se intenta.
    # ">=" significa "mayor o igual que".
    if umbral and _como_tupla(version) >= _como_tupla(umbral):
        return "LOW", f"{firma['service']} {version} igual o posterior al umbral {umbral}"
    # Devolver dos valores separados por coma entrega una tupla: (riesgo, nota).
    return firma["risk"], firma["note"]


def clasificar_banner(banner: str) -> dict:
    """
    Compara un banner con cada firma, en orden, y devuelve la primera que coincide.
    Resultado: diccionario con service, version, risk y note.
    """
    # Las funciones de captura devuelven los errores entre corchetes, como
    # "[Timeout - sin respuesta]": eso no es un banner, así que no se clasifica.
    # "not banner" es verdadero si el texto está vacío. "or" basta con que una
    # de las dos condiciones se cumpla. .startswith("[") pregunta si empieza por "[".
    if not banner or banner.startswith("["):
        return dict(SIN_BANNER)  # dict(...) entrega una COPIA, para no modificar el original
    # "for" repite el bloque sangrado una vez por cada elemento de la lista:
    # en cada vuelta, la variable "firma" toma el valor de la siguiente firma.
    for firma in SIGNATURES:
        # re.search busca el patrón en cualquier parte del banner. Devuelve un
        # resultado ("match") si lo encuentra, o None si no.
        # IGNORECASE: no distingue mayúsculas; MULTILINE: ^ vale al inicio de cada línea.
        # La barra vertical | combina ambas opciones.
        match = re.search(firma["pattern"], banner, re.IGNORECASE | re.MULTILINE)
        if not match:
            continue  # "continue" salta a la siguiente vuelta del for: esta firma no sirve
        grupo = firma["version_group"]
        # match.group(n) devuelve lo que capturó el grupo n; puede ser None si era opcional.
        # A "or B" devuelve A si tiene valor, o B si A es None o vacío.
        # .strip() quita espacios de los extremos y [:60] se queda con los primeros
        # 60 caracteres (un RECORTE: [inicio:fin], aquí desde el principio hasta 60).
        version = (match.group(grupo) or "no expuesta").strip()[:60]
        # Una función que devuelve dos valores se puede recibir en dos variables a la vez.
        riesgo, nota = _riesgo(firma, version)
        return {"service": firma["service"], "version": version, "risk": riesgo, "note": nota}
    # Solo se llega aquí si ninguna firma coincidió (con el comodín final, casi nunca).
    # dict(SIN_BANNER, note=...) copia el diccionario y cambia el valor de "note".
    return dict(SIN_BANNER, note="Banner capturado sin clasificación disponible")
