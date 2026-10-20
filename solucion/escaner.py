"""
escaner.py - Motor de escaneo (Paso 4).

Junta las piezas: para cada puerto captura el banner (captura.py), lo clasifica
(signatures.py) y arma un registro con todos los datos.

Por qué en paralelo: escanear es sobre todo ESPERAR a la red. Revisando un
puerto tras otro, las esperas se suman; con varios HILOS (tareas que avanzan al
mismo tiempo dentro del programa), las esperas ocurren a la vez y el escaneo
termina antes. MAX_WORKERS limita cuántas conexiones simultáneas recibe el
objetivo, para no saturarlo: también es uso responsable.
"""
import concurrent.futures  # incluido en Python: ejecutar tareas en paralelo
from datetime import datetime, timezone  # incluido en Python: fechas y horas

# Funciones y valores de los archivos de los pasos 1, 2 y 3.
from captura import capturar_banner_tcp, capturar_cabeceras_http, sonda_http
from config import MAX_WORKERS, SERVICIOS_HTTP, SOCKET_TIMEOUT
from signatures import clasificar_banner

# Icono de color por nivel de riesgo, para leer la consola de un vistazo.
ICONOS = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢", "INFO": "🔵", "UNKNOWN": "⚪"}


def _capturar_web(host: str, puerto: int, nombre_servicio: str) -> tuple:
    """
    Captura un servicio web. Primero con requests (cabeceras HTTP); si eso falla,
    plan B: envía HEAD "a mano" por un socket y clasifica la respuesta tal cual llega.
    Devuelve una tupla de 3 valores: (banner, cabeceras, código de estado HTTP).
    """
    # "==" COMPARA (pregunta "¿son iguales?") y da True o False; no confundir con "=",
    # que GUARDA un valor. Aquí tls recibe True solo si el servicio es "HTTPS".
    http_data = capturar_cabeceras_http(host, puerto, tls=nombre_servicio == "HTTPS")
    banner = http_data["banner"]
    # "!=" significa "es distinto de".
    if banner.startswith("[") and nombre_servicio != "HTTPS":  # falló y no es cifrado
        crudo = capturar_banner_tcp(host, puerto, sonda=sonda_http(host))
        banner = crudo if not crudo.startswith("[") else banner  # usar el plan B solo si funcionó
    return banner, http_data["headers"], http_data["status"]


def escanear_puerto(host: str, puerto: int, nombre_servicio: str) -> dict:
    """Escanea UN puerto: captura su banner, lo clasifica y devuelve un registro (diccionario)."""
    # Fecha y hora actuales en UTC (hora universal), con formato ISO 8601,
    # por ejemplo "2026-10-20T11:13:26Z". Un MÉTODO es una función que pertenece a
    # un valor y se llama con un punto: "hola".upper() devuelve "HOLA". Aquí los
    # métodos se encadenan: cada uno trabaja sobre el resultado del anterior.
    # .replace("+00:00", "Z") cambia un texto por otro: la zona UTC se escribe "Z".
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    # El tipo de captura se elige por el servicio declarado, no por el número de puerto.
    if nombre_servicio in SERVICIOS_HTTP:
        # Una función que devuelve 3 valores se recibe en 3 variables a la vez, en orden.
        banner_raw, cabeceras, http_status = _capturar_web(host, puerto, nombre_servicio)
    else:  # "else" es el camino contrario: se ejecuta cuando la condición del if es falsa
        # Aquí también van tres valores, uno por variable y en orden: el banner,
        # un diccionario vacío {} (no hay cabeceras) y None (no hay código HTTP).
        banner_raw, cabeceras, http_status = capturar_banner_tcp(host, puerto), {}, None
    clasificacion = clasificar_banner(banner_raw)
    # El registro del puerto: un diccionario escrito en varias líneas para que se lea mejor.
    return {
        "timestamp":        timestamp,
        "host":             host,
        "port":             puerto,
        "expected_service": nombre_servicio,           # lo que esperábamos encontrar
        "banner_raw":       banner_raw[:200],          # el banner tal cual, recortado a 200 caracteres
        "service":          clasificacion["service"],  # lo que realmente se identificó
        "version":          clasificacion["version"],
        "risk":             clasificacion["risk"],
        "risk_note":        clasificacion["note"],     # por qué se asignó ese riesgo
        "http_status":      http_status,               # None si no es un servicio web
        "http_headers":     cabeceras,
    }


def ejecutar_escaneo(host: str, puertos: dict, max_workers: int = MAX_WORKERS) -> list:
    """Escanea todos los puertos en paralelo y devuelve la lista de registros ordenada por puerto."""
    # print muestra un texto en la terminal. \n es un salto de línea.
    # len(puertos) cuenta cuántos elementos tiene el diccionario.
    print(f"\n[*] Iniciando escaneo de {len(puertos)} puertos en {host}")
    print(f"[*] Hilos paralelos: {max_workers} | Timeout por puerto: {SOCKET_TIMEOUT}s")
    print("-" * 60)  # multiplicar un texto lo repite: 60 guiones seguidos
    resultados = []  # lista vacía donde se irán guardando los registros
    # ThreadPoolExecutor crea un grupo de hilos trabajadores; "with" los cierra al terminar.
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # submit entrega una tarea a un hilo y devuelve de inmediato un FUTURO:
        # un objeto que contendrá el resultado cuando la tarea termine.
        # Se arma el diccionario {futuro: (puerto, nombre)} para saber, al final,
        # a qué puerto corresponde cada futuro.
        futuros = {executor.submit(escanear_puerto, host, puerto, nombre): (puerto, nombre)
                   for puerto, nombre in puertos.items()}
        # as_completed entrega cada futuro apenas termina, sin esperar al más lento.
        for futuro in concurrent.futures.as_completed(futuros):
            puerto, nombre = futuros[futuro]  # "desempaca" la tupla en dos variables
            try:
                r = futuro.result()  # el registro que devolvió escanear_puerto
                resultados.append(r)  # .append agrega un elemento al final de la lista
                # Dentro de { } se puede dar formato: :>5 alinea a la derecha en 5
                # espacios y :<8 a la izquierda en 8. Así las columnas quedan parejas.
                # ICONOS.get(clave, "⚪") devuelve "⚪" si la clave no existe.
                print(f"  {ICONOS.get(r['risk'], '⚪')} Puerto {puerto:>5}/tcp  "
                      f"[{r['risk']:<8}]  {r['service']} {r['version'][:30]}")
            # "Exception" atrapa cualquier error: si un puerto falla, se anota y el escaneo sigue.
            except Exception as e:
                print(f"  [!] Puerto {puerto}: Error al procesar resultado - {e}")
                resultados.append({"port": puerto, "expected_service": nombre,
                                   "error": str(e), "risk": "UNKNOWN"})  # str(e): el error como texto
    # Los hilos terminan en cualquier orden: se ordena por número de puerto para el reporte.
    # "lambda x: x.get("port", 0)" es una función de una línea, sin nombre: le dice a
    # sort que use el puerto de cada registro como criterio de orden.
    resultados.sort(key=lambda x: x.get("port", 0))
    return resultados
