<!-- Idioma del documento: es-CO (español de Colombia) -->
# Salidas reales del laboratorio 4

Ejecución del 2026-10-20 en Linux con Python 3.14.8 y requests 2.34.2. Cada bloque muestra el comando y su salida sin editar. El orden de las líneas con iconos del paso 6 cambia en cada ejecución.

## Paso 0: dependencias

```bash
python3 -c "import socket, requests, re, concurrent.futures, json; print('Dependencias OK')"
```

```text
Dependencias OK
(código de salida: 0)
```

## Problema 1: herramienta sin simulador

```bash
python3 banner_grabber.py
```

```text
+--------------------------------------------------------------+
|  BANNER GRABBER - Laboratorio 4 (Uso Educativo)              |
|  Ejecutar SOLO sobre sistemas con autorización escrita       |
+--------------------------------------------------------------+

[*] Objetivo: 127.0.0.1
[*] Puertos a escanear: [10021, 10022, 10025, 10080, 10443, 13306, 18080]

[*] Verificando conectividad con el objetivo...
[!] Ningún puerto responde en 127.0.0.1. Inicie el simulador en otra terminal:
    python3 simulador_metasploitable.py
(código de salida: 1)
```

## Paso 1: configuración

```bash
python3 pasos/paso1_configuracion.py
```

```text
Objetivo (TARGET_HOST): 127.0.0.1
Lista permitida (HOSTS_PERMITIDOS): ['127.0.0.1']

Servicio   Puerto estándar  Puerto local
FTP                     21         10021
SSH                     22         10022
SMTP                    25         10025
HTTP                    80         10080
HTTPS                  443         10443
MySQL                 3306         13306
HTTP-alt              8080         18080

Servicios que se consultan por HTTP: ['HTTP', 'HTTP-alt', 'HTTPS']
Hilos paralelos: 4 | Timeout TCP: 4.0s
(código de salida: 0)
```

## Paso 2: firmas

```bash
python3 pasos/paso2_firmas.py
```

```text
Banner: '220 ProFTPD 1.3.3c Server (Metasploitable)'
  -> Servicio: ProFTPD | Versión: 1.3.3c | Riesgo: CRITICAL

Banner: 'SSH-2.0-OpenSSH_4.7p1 Debian-8ubuntu1'
  -> Servicio: OpenSSH | Versión: 4.7p1 | Riesgo: HIGH

Banner: 'Apache/2.2.8 (Ubuntu) DAV/2'
  -> Servicio: Apache | Versión: 2.2.8 | Riesgo: HIGH

Banner: '220 metasploitable.localdomain ESMTP Postfix '
  -> Servicio: Postfix | Versión: no expuesta | Riesgo: MEDIUM

Banner: 'SSH-2.0-OpenSSH_10.2p1 Ubuntu-2'
  -> Servicio: OpenSSH | Versión: 10.2p1 | Riesgo: LOW

(código de salida: 0)
```

## Simulador: solo escucha en 127.0.0.1

```bash
ss -ltn | grep -E '127.0.0.1:1(0021|0022|0025|0080|3306|8080)'
```

```text
LISTEN 0      5                                   127.0.0.1:18080      0.0.0.0:*
LISTEN 0      5                                   127.0.0.1:10080      0.0.0.0:*
LISTEN 0      5                                   127.0.0.1:10022      0.0.0.0:*
LISTEN 0      5                                   127.0.0.1:10021      0.0.0.0:*
LISTEN 0      5                                   127.0.0.1:10025      0.0.0.0:*
LISTEN 0      5                                   127.0.0.1:13306      0.0.0.0:*
(código de salida: 0)
```

## Paso 3: captura de banners

```bash
python3 pasos/paso3_captura.py
```

```text
=== Prueba FTP (puerto 10021): el servicio habla primero ===
Banner: 220 ProFTPD 1.3.3c Server (ProFTPD Default Installation) [127.0.0.1]

=== Prueba SSH (puerto 10022) ===
Banner: SSH-2.0-OpenSSH_4.7p1 Debian-8ubuntu1

=== Prueba HTTP (puerto 10080): hay que preguntar con HEAD ===
Status: 200
Banner: Apache/2.2.8 (Ubuntu) DAV/2 | PHP/5.2.4-2ubuntu5.10
Cabeceras: {'Server': 'Apache/2.2.8 (Ubuntu) DAV/2', 'X-Powered-By': 'PHP/5.2.4-2ubuntu5.10'}
(código de salida: 0)
```

## Paso 3: banner crudo sin la herramienta

```bash
python3 -c "import socket; s = socket.create_connection(('127.0.0.1', 10025)); print(s.recv(200))"
```

```text
b'220 metasploitable.localdomain ESMTP Postfix (Ubuntu)\r\n'
(código de salida: 0)
```

## Paso 4: un puerto

```bash
python3 pasos/paso4_un_puerto.py
```

```text
Resultado del escaneo del puerto 10022 (SSH):
{
  "timestamp": "2026-10-20T11:44:09Z",
  "host": "127.0.0.1",
  "port": 10022,
  "expected_service": "SSH",
  "banner_raw": "SSH-2.0-OpenSSH_4.7p1 Debian-8ubuntu1",
  "service": "OpenSSH",
  "version": "4.7p1",
  "risk": "HIGH",
  "risk_note": "OpenSSH anterior al umbral 9.8p1 (la que corrige CVE-2024-6387); revise los CVE de esta versión",
  "http_status": null,
  "http_headers": {}
}
(código de salida: 0)
```

## Paso 5: resumen con datos de ejemplo

```bash
python3 pasos/paso5_reporte.py
```

```text

======================================================================
  REPORTE DE BANNER GRABBING - Objetivo: 127.0.0.1
======================================================================

Puerto   Servicio       Versión                   Riesgo     Estado HTTP
----------------------------------------------------------------------
10021    ProFTPD        1.3.3c                    CRITICAL   -
10022    OpenSSH        4.7p1                     HIGH       -
10080    Apache         2.2.8                     HIGH       200

----------------------------------------------------------------------
  DISTRIBUCIÓN DE RIESGO:
    CRITICAL  : # (1)
    HIGH      : ## (2)

  [!] ATENCIÓN: 1 servicio(s) con riesgo CRÍTICO detectado(s).
  [!] 2 servicio(s) con riesgo ALTO detectado(s).

  SERVICIOS IDENTIFICADOS:
    - ProFTPD 1.3.3c
    - OpenSSH 4.7p1
    - Apache 2.2.8
======================================================================

(código de salida: 0)
```

## Paso 6: escaneo completo

```bash
python3 banner_grabber.py
```

```text
+--------------------------------------------------------------+
|  BANNER GRABBER - Laboratorio 4 (Uso Educativo)              |
|  Ejecutar SOLO sobre sistemas con autorización escrita       |
+--------------------------------------------------------------+

[*] Objetivo: 127.0.0.1
[*] Puertos a escanear: [10021, 10022, 10025, 10080, 10443, 13306, 18080]

[*] Verificando conectividad con el objetivo...
[+] Objetivo 127.0.0.1 alcanzable.
[!] Los reportes contienen IP, banners y versiones: trátelos como datos sensibles.

[*] Iniciando escaneo de 7 puertos en 127.0.0.1
[*] Hilos paralelos: 4 | Timeout por puerto: 4.0s
------------------------------------------------------------
  🔴 Puerto 10021/tcp  [CRITICAL]  ProFTPD 1.3.3c
  🟠 Puerto 10022/tcp  [HIGH    ]  OpenSSH 4.7p1
  🟡 Puerto 10025/tcp  [MEDIUM  ]  Postfix no expuesta
  🔴 Puerto 13306/tcp  [CRITICAL]  MySQL 5.0.51a
  🟠 Puerto 10080/tcp  [HIGH    ]  Apache 2.2.8
  ⚪ Puerto 10443/tcp  [UNKNOWN ]  N/A N/A
  🟠 Puerto 18080/tcp  [HIGH    ]  Apache 2.2.8

======================================================================
  REPORTE DE BANNER GRABBING - Objetivo: 127.0.0.1
======================================================================

Puerto   Servicio       Versión                   Riesgo     Estado HTTP
----------------------------------------------------------------------
10021    ProFTPD        1.3.3c                    CRITICAL   -
10022    OpenSSH        4.7p1                     HIGH       -
10025    Postfix        no expuesta               MEDIUM     -
10080    Apache         2.2.8                     HIGH       200
10443    N/A            N/A                       UNKNOWN    -
13306    MySQL          5.0.51a                   CRITICAL   -
18080    Apache         2.2.8                     HIGH       200

----------------------------------------------------------------------
  DISTRIBUCIÓN DE RIESGO:
    CRITICAL  : ## (2)
    HIGH      : ### (3)
    MEDIUM    : # (1)
    UNKNOWN   : # (1)

  [!] ATENCIÓN: 2 servicio(s) con riesgo CRÍTICO detectado(s).
  [!] 3 servicio(s) con riesgo ALTO detectado(s).

  SERVICIOS IDENTIFICADOS:
    - ProFTPD 1.3.3c
    - OpenSSH 4.7p1
    - Postfix no expuesta
    - Apache 2.2.8
    - MySQL 5.0.51a
    - Apache 2.2.8
======================================================================

[+] Reporte guardado en: output/banner_report_127_0_0_1_20261020_114409_767401.json
[*] Escaneo completado.

(código de salida: 0)
```

## Paso 7: validación 7.1, 7.2 y 7.3

```bash
python3 validar.py
```

```text
  JSON válido: output/banner_report_127_0_0_1_20261020_114409_767401.json

7.1 Reporte JSON
  PASS | Puertos escaneados: obtenido=7 esperado=7
  PASS | Objetivo: obtenido='127.0.0.1' esperado='127.0.0.1'
  PASS | Servicios CRITICAL: obtenido=2 esperado=2
  PASS | Servicios HIGH: obtenido=3 esperado=3

7.2 Clasificación de banners
  PASS | '220 ProFTPD 1.3.3c Server': obtenido=('ProFTPD', '1.3.3c', 'CRITICAL') esperado=('ProFTPD', '1.3.3c', 'CRITICAL')
  PASS | '220 (vsFTPd 2.3.4)': obtenido=('vsftpd', '2.3.4', 'CRITICAL') esperado=('vsftpd', '2.3.4', 'CRITICAL')
  PASS | 'SSH-2.0-OpenSSH_4.7p1 Debian': obtenido=('OpenSSH', '4.7p1', 'HIGH') esperado=('OpenSSH', '4.7p1', 'HIGH')
  PASS | 'SSH-2.0-OpenSSH_10.2p1 Ubuntu': obtenido=('OpenSSH', '10.2p1', 'LOW') esperado=('OpenSSH', '10.2p1', 'LOW')
  PASS | '220 metasploitable.localdomain': obtenido=('Postfix', 'no expuesta', 'MEDIUM') esperado=('Postfix', 'no expuesta', 'MEDIUM')
  PASS | 'Apache/2.2.8 (Ubuntu) DAV/2 | ': obtenido=('Apache', '2.2.8', 'HIGH') esperado=('Apache', '2.2.8', 'HIGH')
  PASS | 'Apache/2.4.62 (Debian)': obtenido=('Apache', '2.4.62', 'LOW') esperado=('Apache', '2.4.62', 'LOW')
  PASS | '!\x00\x00\x00\n5.0.51a-3ubuntu5\x00\x08\x00\x00\x00abcd': obtenido=('MySQL', '5.0.51a', 'CRITICAL') esperado=('MySQL', '5.0.51a', 'CRITICAL')
  PASS | '': obtenido=('N/A', 'N/A', 'UNKNOWN') esperado=('N/A', 'N/A', 'UNKNOWN')

7.3 Banners crudos (ascii() muestra los bytes de control sin romper la línea)
    Puerto 10021: '220 ProFTPD 1.3.3c Server (ProFTPD Default Installation) [127.0.0.1]'
    Puerto 10022: 'SSH-2.0-OpenSSH_4.7p1 Debian-8ubuntu1'
    Puerto 10025: '220 metasploitable.localdomain ESMTP Postfix (Ubuntu)'
    Puerto 10080: 'Apache/2.2.8 (Ubuntu) DAV/2 | PHP/5.2.4-2ubuntu5.10'
    Puerto 13306: '!\x00\x00\x00\n5.0.51a-3ubuntu5\x00\x08\x00\x00\x00abcdefgh\x00,\ufffd'
    Puerto 18080: 'Apache/2.2.8 (Ubuntu) DAV/2 | PHP/5.2.4-2ubuntu5.10'
  PASS | Puertos con banner: obtenido=6 esperado=6

Resultado final: TODO PASA
(código de salida: 0)
```

## Problema 2: HEAD rechazado (curl)

```bash
curl -sS -I --max-time 3 http://127.0.0.1:10080/
```

```text
curl: (52) Empty reply from server
(código de salida: 52)
```

## Problema 2: la herramienta reintenta con GET

```bash
python3 -c "from escaner import escanear_puerto; r = escanear_puerto('127.0.0.1', 10080, 'HTTP'); print(r['service'], r['version'], r['risk'], r['http_status'])"
```

```text
Apache 2.2.8 HIGH 200
(código de salida: 0)
```

## Pruebas automáticas

```bash
python3 -W error -m unittest -v test_firmas test_captura_local test_seguridad
```

```text
test_banner_desconocido (test_firmas.FirmasTest.test_banner_desconocido) ... ok
test_banner_vacio_o_error (test_firmas.FirmasTest.test_banner_vacio_o_error) ... ok
test_clasificacion_basica (test_firmas.FirmasTest.test_clasificacion_basica) ... ok
test_ftp_generico_sigue_funcionando (test_firmas.FirmasTest.test_ftp_generico_sigue_funcionando) ... ok
test_mysql_en_texto_plano (test_firmas.FirmasTest.test_mysql_en_texto_plano) ... ok
test_mysql_por_handshake_binario (test_firmas.FirmasTest.test_mysql_por_handshake_binario) ... ok
test_postfix_con_version_la_captura (test_firmas.FirmasTest.test_postfix_con_version_la_captura) ... ok
test_proftpd_conserva_letra_de_version (test_firmas.FirmasTest.test_proftpd_conserva_letra_de_version) ... ok
test_riesgo_depende_de_la_version (test_firmas.FirmasTest.test_riesgo_depende_de_la_version) ... ok
test_smtp_generico_no_es_ftp (test_firmas.FirmasTest.test_smtp_generico_no_es_ftp) ... ok
test_smtp_no_se_confunde_con_ftp (test_firmas.FirmasTest.test_smtp_no_se_confunde_con_ftp) ... ok
test_cabeceras_http_locales (test_captura_local.CapturaLocalTest.test_cabeceras_http_locales) ... ok
test_head_rechazado_usa_get (test_captura_local.CapturaLocalTest.test_head_rechazado_usa_get) ... ok
test_http_en_puerto_alto_se_detecta (test_captura_local.CapturaLocalTest.test_http_en_puerto_alto_se_detecta) ... ok
test_https_cerrado_queda_unknown (test_captura_local.CapturaLocalTest.test_https_cerrado_queda_unknown) ... ok
test_mysql_handshake_local (test_captura_local.CapturaLocalTest.test_mysql_handshake_local) ... ok
test_puerto_cerrado_se_reporta (test_captura_local.CapturaLocalTest.test_puerto_cerrado_se_reporta) ... ok
test_sin_banner_da_timeout (test_captura_local.CapturaLocalTest.test_sin_banner_da_timeout) ... ok
test_smtp_local (test_captura_local.CapturaLocalTest.test_smtp_local) ... ok
test_ssh_local_se_clasifica (test_captura_local.CapturaLocalTest.test_ssh_local_se_clasifica) ... ok
test_columna_http_muestra_guion (test_seguridad.SeguridadTest.test_columna_http_muestra_guion) ... ok
test_http_fuera_de_lista_no_envia_peticion (test_seguridad.SeguridadTest.test_http_fuera_de_lista_no_envia_peticion) ... ok
test_main_rechaza_objetivo_no_permitido (test_seguridad.SeguridadTest.test_main_rechaza_objetivo_no_permitido) ... ok
test_no_sigue_redirecciones (test_seguridad.SeguridadTest.test_no_sigue_redirecciones) ... ok
test_solo_loopback_permitido (test_seguridad.SeguridadTest.test_solo_loopback_permitido) ... ok
test_tcp_fuera_de_lista_no_abre_socket (test_seguridad.SeguridadTest.test_tcp_fuera_de_lista_no_abre_socket) ... ok

----------------------------------------------------------------------
Ran 26 tests in 3.523s

OK
(código de salida: 0)
```

## Calidad: lint y líneas de código

```bash
ruff check --no-cache . && shellcheck *.sh && echo 'shellcheck sin avisos' && python3 ../herramientas/comprobar_guia.py
```

```text
All checks passed!
shellcheck sin avisos
PASS | config.py: idéntico a solucion/, 30 líneas de código de 121 en total
PASS | signatures.py: idéntico a solucion/, 57 líneas de código de 179 en total
PASS | captura.py: idéntico a solucion/, 61 líneas de código de 148 en total
PASS | escaner.py: idéntico a solucion/, 54 líneas de código de 111 en total
PASS | report.py: idéntico a solucion/, 64 líneas de código de 108 en total
PASS | banner_grabber.py: idéntico a solucion/, 40 líneas de código de 91 en total
(código de salida: 0)
```

## Paso 9: limpieza

```bash
./limpiar.sh --borrar-reportes
```

```text
[=] El simulador no estaba corriendo
output/banner_report_127_0_0_1_20261020_114409_767401.json
[+] Reportes borrados
[+] Sin procesos del laboratorio activos
(código de salida: 0)
```

## Control de cambios

| Versión | Fecha | Autor | Descripción del cambio |
|---|---|---|---|
| 1.0.0 | 2026-10-20 | Andrés García | Salidas reales de la ejecución completa del laboratorio. |
