<!-- Idioma del documento: es-CO (español de Colombia) -->
# Laboratorio 4: herramienta de banner grabbing en Python

Curso Hacking con Python, capítulo 4: fingerprinting de servicios.

En este laboratorio usted construye en Python una herramienta que se conecta a puertos TCP (Transmission Control Protocol, protocolo de control de transmisión), lee cómo se presenta cada servicio (su *banner*), identifica producto y versión con expresiones regulares, asigna un nivel de riesgo y genera un reporte JSON (JavaScript Object Notation, formato de texto para datos estructurados).

Todo ocurre **en su propio equipo, sin máquinas virtuales**. Un simulador incluido imita a Metasploitable 2, una máquina de práctica con servicios antiguos que se usa en cursos de seguridad: publica sus banners en `127.0.0.1`, y ningún paquete sale de su computador.

## Dos lados: la práctica y la respuesta

| Carpeta | Qué contiene | Quién la usa |
|---|---|---|
| [`paso-a-paso/`](paso-a-paso/) | **La práctica.** La guía [`paso-a-paso/README.md`](paso-a-paso/README.md) y el material de apoyo (simulador, comprobaciones por paso, validación y pruebas). Usted crea los seis archivos de la herramienta pegando el código de la guía, comentado línea a línea para quien ve Python por primera vez. | Estudiante |
| [`solucion/`](solucion/) | **La respuesta.** Los seis archivos terminados y el laboratorio completo funcionando, con sus salidas reales en [`solucion/output.md`](solucion/output.md). | Estudiante que quiera comparar, e instructor |

Recomendación: haga primero la práctica y abra la solución solo para comparar cuando algo no le funcione (`diff config.py ../solucion/config.py`).

## Empezar

```bash
git clone https://github.com/andresgarcia0313/pyhacklabcap4.git
cd pyhacklabcap4/paso-a-paso
```

Luego abra [`paso-a-paso/README.md`](paso-a-paso/README.md) y siga el Paso 0.

¿Solo quiere ver la herramienta funcionando? Desde la carpeta `pyhacklabcap4`, ejecute la solución:

```bash
cd solucion
./ejecutar_laboratorio.sh
```

## Qué va a aprender

1. Capturar banners de servicios TCP con el módulo `socket`.
2. Extraer cabeceras HTTP (Hypertext Transfer Protocol, protocolo de transferencia de hipertexto) con `requests` para identificar servidores web.
3. Clasificar banners con expresiones regulares y un diccionario de firmas.
4. Escanear en paralelo con `concurrent.futures` sin saturar al objetivo.
5. Generar un reporte JSON con servicio, versión y nivel de riesgo.
6. Aplicar controles de uso responsable: lista permitida de destinos y manejo de datos sensibles.

No necesita saber Python: la guía y los comentarios del código lo explican desde cero. Requisitos: Python 3.10 o superior en Linux, macOS o Windows con WSL (Windows Subsystem for Linux, subsistema de Linux para Windows). El detalle está en la guía.

## Para el instructor

- `./comprobar_repositorio.sh`: verifica que el material de apoyo sea igual en ambas carpetas y que el código de la guía sea idéntico al de la solución. Además ejecuta el laboratorio completo dos veces, con la solución y con el código copiado de la guía, como lo haría un estudiante. Debe terminar en `REPOSITORIO CORRECTO`.
- `herramientas/comprobar_guia.py`: la parte de esa verificación que compara la guía con la solución y cuenta las líneas de código de cada archivo.

## Uso responsable

Use esta herramienta solo sobre sistemas con autorización escrita. No escanee redes ajenas ni la red de su casa u oficina. La lista permitida del laboratorio contiene solo `127.0.0.1`.

## Control de cambios

| Versión | Fecha | Autor | Descripción del cambio |
|---|---|---|---|
| 1.0.0 | 2026-10-20 | Andrés García | Laboratorio 4 de banner grabbing en ejecución local, con simulador, pruebas automáticas y guía. |
| 1.1.0 | 2026-10-20 | Andrés García | Dos carpetas: `paso-a-paso/` para que el estudiante construya la herramienta y `solucion/` con la respuesta. Comprobación integral del repositorio. |
| 1.2.0 | 2026-10-20 | Andrés García | Código comentado para quien ve Python por primera vez; no se requieren conocimientos previos de Python. |
