<!-- Idioma del documento: es-CO (español de Colombia) -->
# Solución del laboratorio 4

Esta carpeta es **la respuesta**: la herramienta terminada y funcionando. Si todavía no hace la práctica, empiece por la guía [`../paso-a-paso/README.md`](../paso-a-paso/README.md) y vuelva aquí solo para comparar.

## Ejecutarla

```bash
./ejecutar_laboratorio.sh
```

Prepara el entorno, corre las 26 pruebas, levanta el simulador, escanea, valida el reporte, reproduce el Problema 2 de la guía (Paso 8) y limpia. Debe terminar con `LABORATORIO COMPLETADO`. Las salidas reales de cada paso están en [`output.md`](output.md).

## Los seis archivos de la respuesta

| Archivo | Paso de la guía | Qué hace |
|---|---|---|
| `config.py` | 1 | Objetivo, puertos, tiempos de espera, niveles de riesgo y lista permitida. |
| `signatures.py` | 2 | Firmas con expresiones regulares, extracción de versión y riesgo por umbral. |
| `captura.py` | 3 | Captura de banners por TCP (Transmission Control Protocol, protocolo de control de transmisión) y de cabeceras por HTTP (Hypertext Transfer Protocol, protocolo de transferencia de hipertexto). |
| `escaner.py` | 4 | Escaneo de un puerto y escaneo paralelo con hilos. |
| `report.py` | 5 | Reporte JSON (JavaScript Object Notation, formato de texto para datos estructurados) y resumen en consola. |
| `banner_grabber.py` | 6 | Programa principal: valida, escanea, resume y guarda. |

El resto de archivos es el mismo material de apoyo de `paso-a-paso/`: simulador, comprobaciones por paso, validación, pruebas y scripts.

## Comparar con su trabajo

Desde `paso-a-paso/`:

```bash
diff signatures.py ../solucion/signatures.py
```

Si no hay salida, su archivo es idéntico a la respuesta. Si hay diferencias, no siempre son errores: lo que cuenta es que `python3 validar.py` y las pruebas pasen.

## Control de cambios

| Versión | Fecha | Autor | Descripción del cambio |
|---|---|---|---|
| 1.0.0 | 2026-10-20 | Andrés García | Solución del laboratorio 4 separada de la guía paso a paso. |
