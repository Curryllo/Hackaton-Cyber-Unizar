# CYBERARENA - Proyecto del equipo *zeroday*
# 🛡️ Detección y Análisis Automatizado de Amenazas con T-Pot y TheHive

Este proyecto implementa un sistema automatizado de inteligencia de amenazas, utilizando el honeypot **T-Pot** para la recolección de ataques de bajo nivel y **TheHive** para la gestión y el análisis de incidentes. 

---

## 💡 El Reto: Detección y Análisis Automatizado de Amenazas

La rápida detección y respuesta a los ataques de red de bajo nivel (como escaneos, intentos de login por fuerza bruta y explotación de vulnerabilidades conocidas) es fundamental en la seguridad.

El objetivo de este proyecto es:

> **Implementar un sistema automatizado para la detección, recolección y análisis de ataques de bajo nivel** dirigidos a servicios de red comunes, utilizando un **honeypot** para engañar a los atacantes y un **sistema de inteligencia de amenazas** para procesar la información.

### Componentes Clave

| Herramienta | Tipo | Descripción |
| :--- | :--- | :--- |
| **T-Pot (The Honeypot)** | Plataforma de Inteligencia de Amenazas | Diseñada para instalar, configurar y orquestar una gran cantidad de honeypots de baja y media interacción de forma rápida y sencilla. |
| **TheHive** | Marco de Gestión de Incidentes (SIRP) | Diseñado para la colaboración, la centralización de datos y el análisis de incidentes de seguridad e inteligencia de amenazas. |

---

## 🛠️ La Solución: Arquitectura e Implementación

La solución se compone de dos despliegues principales (T-Pot y TheHive) integrados mediante **ElastAlert2**, y asegurados con un *proxy inverso* y **Cloudflare**.

### 1. Despliegue de TheHive (Gestión de Incidentes)

TheHive se desplegó rápidamente utilizando Docker para asegurar una versión estable y controlada.

* **Versión Elegida:** `5.4.6-1`
* **IP Interna:** `192.168.0.16`
* **Sistema Operativo:** `Ubuntu Server`
* **Comando de Despliegue:**
    ```bash
    docker pull strangebee/thehive:5.4.6-1
    sudo docker run -d --name thehive \
    -p 9000:9000 \
    strangebee/thehive:5.4.6-1
    ```
* **Hardware:** Lenovo (8GB RAM, 1TB Almacenamiento, 4 Cores) - Ubicada en la casa de uno de los integrantes del equipo.
* **Acceso Inicial:** `https://thehive.eslus.org` (Puerto interno `9000`).
* **Usuario Admin:** Se utilizó la cuenta de administrador para la configuración inicial de TheHive.
* **Organización:** Se creó la organización **`Hackaton`** en TheHive.
* **Usuario de Análisis:** Se creó el usuario **`Zeroday`** con permisos de **analista** para gestionar los casos y alertas dentro de la organización Hackaton.

#### Configuración Previa de TheHive

Para que los scripts de ElastAlert2 funcionen correctamente, es necesario configurar tipos de observables personalizados en TheHive (se realizó desde la cuenta de administrador):

1. **Crear Observable Type `account`:**
   - Ir a: **Gestión de entidades > Tipo observables > Añadir tipo de observable**
   - Crear nuevo tipo con nombre: `account`
   - Descripción: "Cuenta de usuario comprometida"
   - Se utiliza para representar nombres de usuario atacados

2. **Crear Observable Type `region`:**
   - Ir a: **Gestión de entidades > Tipo observables > Añadir tipo de observable**
   - Crear nuevo tipo con nombre: `region`
   - Descripción: "Región geográfica de origen"
   - Se utiliza para representar regiones de donde provienen los ataques

3. **Generar API Key:**
   - Ir a: **Ajustes > Clave API**
   - Crear una nueva API Key (desde la cuenta del analista)
   - Copiar el valor y guardarlo en `src/elastalert/scripts/thehive_methods.py` en la variable `thehive_api_key`

4. **Asignar permisos al usuario Zeroday:**
   - Rol: **Analyst** (Analista)
   - Permisos: Lectura y escritura de casos, alertas y tareas
   - Organización: **Hackaton**

### 2. Despliegue de T-Pot (Plataforma de Honeypot)

T-Pot se instaló en una máquina virtual dedicada con los recursos necesarios para orquestar múltiples honeypots.

* **Versión T-Pot:** `24.04.1`
* **Plataforma Host:** N100 (16GB RAM, 526GB Almacenamiento, 4 Cores) bajo OpenNebula - Ubicada en la casa de uno de los integrantes del equipo.
* **VM (Debian 12) Requisitos:** 8GB RAM, 254GB Espacio, 4 CPUs.
* **IP Interna:** `192.168.0.101`
* **Pasos de Instalación:**
    ```bash
    sudo apt update
    sudo apt install git
    git clone [https://github.com/telekom-security/tpotce](https://github.com/telekom-security/tpotce)
    cd tpotce
    ./install.sh
    sudo reboot
    ```
* **Acceso Remoto:** El puerto SSH cambia automáticamente para liberar el puerto 22, utilizado por un honeypot.
    ```bash
    ssh -p 64295 root@192.168.0.101
    ```
* **URL de Acceso:** `https://tpot.eslus.org` (Puerto interno `64297`)
* **Componentes internos de T-Pot:**
  - **Elasticsearch:** `8.19.2` - Almacena todos los eventos y logs de los honeypots (Puerto: 9200)
  - **Kibana:** Panel de visualización integrado en T-Pot para análisis de eventos (Puerto: 5601)
  - **Acceso local:** En la máquina T-Pot se puede acceder directamente a:
    - Elasticsearch: `http://localhost:9200`
    - Kibana: `http://localhost:5601`

### 3. Integración Automatizada (ElastAlert2)

La clave de la automatización reside en **ElastAlert2**, que actúa como un puente entre la inteligencia de T-Pot y el análisis en TheHive.

* **Función:** ElastAlert2 monitoriza el *Elasticsearch* de T-Pot, lee los datos de actividad sospechosa y, mediante *scripts*, interactúa con la API de TheHive.
* **Frecuencia:** Los datos se recogen y procesan cada cierto tiempo configurable.
* **Salida a TheHive:** Creación de **Casos** y **Alertas** para la actividad detectada (inicialmente enfocada en los logs del honeypot **Cowrie**).

### 4. Publicación y Seguridad (HAProxy y Cloudflare)

Se utiliza un *proxy inverso* y un CDN para publicar los servicios de forma segura a través de HTTPS.

* **HAProxy:** Desplegado en el host de TheHive para gestionar el tráfico.
* **Cloudflare:** Proporciona los certificados SSL/TLS, permitiendo el acceso seguro a través de los siguientes dominios:
    * `https://thehive.eslus.org`
    * `https://tpot.eslus.org`
* **Certificados:** Almacenados en `/etc/haproxy/certs`.

---

## 🔧 Especificaciones Técnicas

### Versiones de Software

| Componente | Versión | Descripción |
| :--- | :--- | :--- |
| **T-Pot** | `24.04.1` | Plataforma orchestrada de honeypots |
| **Elasticsearch** | `8.19.2` | Motor de búsqueda y almacenamiento de eventos |
| **Kibana** | Integrada en T-Pot | Visualización de datos de Elasticsearch |
| **TheHive** | `5.4.6-1` | Plataforma de gestión de incidentes |
| **ElastAlert2** | Última versión oficial | Motor de detección y alerta |
| **Debian** | `12` | Sistema operativo de T-Pot |
| **Ubuntu Server** | LTS | Sistema operativo de TheHive |

### Configuración de Red

| Servicio | IP Interna | Puerto Externo | Puerto Interno | Protocolo |
| :--- | :--- | :--- | :--- | :--- |
| **T-Pot** | `192.168.0.101` | SSH: 64295 | SSH: 22 | SSH |
| **T-Pot (Web/Nginx)** | `192.168.0.101` | HTTPS: 443  | 64297 | HTTPS |
| **Kibana (T-Pot)** | `192.168.0.101` | 64296 (local) | 5601 | HTTP |
| **Elasticsearch (T-Pot)** | `192.168.0.101` | 64298 (local) | 9200 | HTTP |
| **Cowrie SSH Honeypot** | `192.168.0.101` | 22-23 | 22-23 | SSH |
| **TheHive** | `192.168.0.16` | HTTPS: 443 | 9000 | HTTPS |


### Índices de Elasticsearch 

Los eventos de T-Pot se almacenan en índices siguiendo este patrón:

- **Patrón:** `logstash-YYYY.MM.DD` (ejemplo: `logstash-2025-12-03`)
- **Índices activos:** Se crean automáticamente cada día
- **Recolección:** Todos los honeypots escriben en el mismo Elasticsearch centralizado
- **Campos principales de eventos Cowrie:**
  - `eventid`: Identificador del evento (ej: `cowrie.session.connect`)
  - `username`: Usuario del intento de acceso
  - `src_ip`: IP origen del atacante
  - `geoip.as_org`: ASN/Organización de la IP
  - `geoip.country_name`: País de origen
  - `geoip_ext.region_name`: Región de origen
  - `@timestamp`: Timestamp del evento

### Honeypots Activos en T-Pot 24.04.1

T-Pot orquesta múltiples honeypots de baja y media interacción. Los principales activos son:

| Honeypot | Puerto(s) | Descripción | Servicio Simulado |
| :--- | :--- | :--- | :--- |
| **Cowrie** | 22-23 | Honeypot SSH de media interacción | OpenSSH |
| **Dionaea** | 20-21, 42, 81, 135, 445, 1433, 1723, 1883, 3306, 27017, 69 | Honeypot multi-protocolo | FTP, TFTP, HTTP, RPC, SMB, MSSQL, PPTP, MQTT, MySQL, MongoDB |
| **Heralding** | 110, 143, 465, 993, 995, 1080, 5432, 5900 | Captura de credenciales | POP3, IMAP, SMTP, SOCKS, PostgreSQL, VNC |
| **SNARE** | 80 | Honeypot web en PHP | Sitio web vulnerable |
| **Wordpot** | 8080 | Honeypot WordPress | Réplica WordPress vulnerable |
| **IPPHoney** | 631 | Honeypot de impresora | CUPS/IPP |
| **Honeytrap** | Varios | Honeypot genérico TCP | Servicios desconocidos |

**Datos recibidos por ElastAlert2:**
- ElastAlert2 monitoriza principalmente los eventos de **Cowrie** para crear alertas en TheHive
- Se pueden añadir nuevas reglas para otros honeypots siguiendo el patrón de `cowrie.yaml`

---

| Parámetro | Valor | Descripción |
| :--- | :--- | :--- |
| **Frecuencia ElastAlert2** | 1 minuto | Se ejecuta cada minuto para buscar nuevos eventos |
| **Buffer de búsqueda** | 15 minutos | Ventana hacia atrás para agrupar eventos |
| **TTL de alertas** | 2 días | Tiempo que se mantienen activas las alertas |
| **Reintentos (crear alerta)** | 3 intentos | Con 5 segundos de espera entre intentos |
| **Reintentos (crear caso)** | Indefinidos | Reintenta cada 5 segundos hasta lograrlo |
| **Re-alerta por IP** | 24 horas | No re-alerta de la misma IP en 24 horas |

---

## 🚀 Uso del Sistema

El sistema opera de forma continua, ejecutando el ciclo de vida del incidente de forma automática:

1.  **Ataque:** Un actor malicioso interactúa con un servicio del honeypot de T-Pot (ej. intenta login en Cowrie).
2.  **Detección y Recolección:** T-Pot registra el evento en su *Elasticsearch*.
3.  **Alerta (ElastAlert2):** ElastAlert2 detecta el nuevo log en Cowrie y dispara un *script* que usa la API de TheHive.
4.  **Creación de Casos/Alertas (TheHive):** Se crea automáticamente un nuevo Caso y/o Alerta en TheHive.
5.  **Análisis (Usuario Zeroday):** El analista (**Zeroday**) accede a TheHive, revisa el Caso creado, enriquece la información y ejecuta las acciones de respuesta (cerrar, escalar, investigar, etc.).

Este flujo asegura que el analista no tenga que pasar tiempo buscando actividad sospechosa, sino que se concentre únicamente en la **investigación y respuesta** de los incidentes ya clasificados.

---

## 📋 Descripción Técnica de los Scripts

### 1. `alerta_cowrie_login.py` - Creación de Alertas Individuales

**Función:** Se ejecuta cada vez que ElastAlert2 detecta un evento de login en Cowrie. Crea una **alerta individual** en TheHive.

**Proceso:**
1. Recibe parámetros desde ElastAlert2 (usuario, IP, ASN, país, región, timestamp)
2. Genera un identificador único basado en timestamp
3. Construye la estructura de datos de la alerta con observables
4. Envía la alerta a TheHive mediante API REST

**Parámetros aceptados:**
- `--user`: Usuario que intentó acceder
- `--remip`: IP origen del ataque
- `--as_org`: ASN/Organización de la IP
- `--country`: País origen
- `--region`: Región origen
- `--timestamp`: Fecha/hora del evento

**Observables generados:**
- `account`: Nombre de usuario atacado
- `ip`: IP del atacante
- `autonomous-system`: ASN de la organización
- `region`: Región geográfica

**Nota importante:** Los tipos de observable `account` y `region` son personalizados en TheHive y debieron ser creados manualmente en la configuración de TheHive para que los scripts pudieran utilizarlos. Estos tipos se pueden crear en:
- **TheHive > Gestión de entidades > Tipo observables > Añadir tipo de observable**
- **Tipo `account`:** Para representar cuentas de usuario comprometidas
- **Tipo `region`:** Para representar regiones geográficas de origen de ataques

---

### 2. `caso_cowrie_login.py` - Creación de Casos Diarios Resumidos

**Función:** Agrega todas las alertas de Cowrie de las últimas 24 horas en un **caso único** con estadísticas consolidadas.

**Proceso:**
1. Consulta TheHive buscando alertas de Cowrie etiquetadas con `cowrie` y estado `New` de las últimas 24 horas
2. Extrae información de cada alerta (usuario, IP, ASN, país, región)
3. Calcula estadísticas:
   - Total de eventos
   - IPs únicas
   - Usuarios atacados
   - ASNs/organizaciones
   - Países y regiones
4. Crea un caso único con título como `Resumen de Login de Cowrie - YYYY-MM-DD HH:MM:SS`
5. Vincula todas las alertas al caso creado
6. Incluye observables consolidados (todas las IPs, usuarios, ASNs, etc.)

**Características:**
- Reintento automático si falla la conexión (cada 5 segundos indefinidamente)
- Timestamp de primer y último evento del rango
- Severidad: Media (nivel 2)
- Estado inicial: `New`
- Etiquetas: `cowrie`, `honeypot`, `brute-force`, `ssh`, `daily-report`

---

### 3. `thehive_methods.py` - Módulo de Integración con TheHive

**Función:** Proporciona funciones reutilizables para interactuar con la API de TheHive.

**Funciones principales:**

#### `crear_alerta(alert_data, max_retries=3, retry_delay=5)`
- **Parámetros:**
  - `alert_data`: Diccionario con los datos de la alerta
  - `max_retries`: Número máximo de reintentos (defecto: 3)
  - `retry_delay`: Segundos entre reintentos (defecto: 5)
- **Retorna:** JSON con la alerta creada o `None` si falla
- **Manejo de errores:** Reintenta automáticamente con espera entre intentos

#### `crear_caso(titulo, descripcion, observables, severity, tags, status)`
- **Parámetros:**
  - `titulo`: Título del caso
  - `descripcion`: Descripción detallada
  - `observables`: Lista de observables a incluir
  - `severity`: Nivel de severidad (1-3)
  - `tags`: Lista de etiquetas
  - `status`: Estado inicial del caso
- **Retorna:** JSON con el caso creado o `None` si falla

#### `vincular_caso_a_alerta(caso_id, alerta_id)`
- **Parámetros:** ID del caso e ID de la alerta
- **Retorna:** JSON con información del vinculado o `None` si falla
- **Función:** Crea la relación entre una alerta y un caso existente

#### `crear_caso_cowrie_24h()`
- **Función:** Orquesta todo el proceso de búsqueda, agregación y creación de casos diarios
- **Sin parámetros**
- **Retorna:** `True` si éxito, `False` si falla

**Configuración requerida (líneas 5-6):**
```python
thehive_url = 'XXXXXXXX'      # URL de la instancia TheHive (ej: https://thehive.eslus.org)
thehive_api_key = 'XXXXXXXX'  # API Key de TheHive (generar desde TheHive > Settings > API Keys)
```

---

### 4. `cowrie.yaml` - Regla de ElastAlert2

**Función:** Define cómo ElastAlert2 detecta eventos de Cowrie en Elasticsearch.

**Configuración:**

- **Tipo:** `frequency` - Dispara cuando detecta al menos N eventos en un timeframe
- **Índice:** `logstash-*` - Busca en todos los índices de Logstash
- **Filtro:** Busca eventos con `eventid:cowrie.*`
- **Campos monitoreados:**
  - `username`: Usuario del intento de acceso
  - `src_ip`: IP origen
  - `geoip.as_org`: ASN/Organización
  - `geoip.country_name`: País
  - `geoip_ext.region_name`: Región
  - `@timestamp`: Fecha/hora del evento

- **Parámetros de disparo:**
  - `num_events: 1` - Se dispara con 1 evento
  - `timeframe: 60 minutos` - Busca en última hora
  - `query_key: ["src_ip"]` - Agrupa por IP origen
  - `realert: 1440 minutos` - No re-alerta de la misma IP en 24h

- **Acción:** Ejecuta `alerta_cowrie_login.py` con los parámetros extraídos de Elasticsearch

---

### 5. `config.yaml` - Configuración de ElastAlert2

**Parámetros clave:**

```yaml
rules_folder: /opt/elastalert/rules              # Donde ElastAlert2 busca las reglas
es_host: elasticsearch                           # Host de Elasticsearch
es_port: 9200                                    # Puerto de Elasticsearch
use_ssl: False                                   # Usar HTTPS (deshabilitado para pruebas)
run_every: minutes: 1                            # Ejecutar búsqueda cada minuto
buffer_time: minutes: 15                         # Ventana de búsqueda: últimos 15 min
verify_certs: False                              # No verificar certificados SSL
writeback_index: elastalert_alerts               # Índice donde guarda su estado
alert_time_limit: days: 2                        # Mantener alertas 2 días
ssl_show_warn: False                             # No mostrar advertencias SSL
```

---

### 6. `Dockerfile` - Imagen Personalizada de ElastAlert2

**Base:** `jertel/elastalert2` - Imagen oficial de ElastAlert2

**Personalización:**
- Usuario: `elastalert` (sin privilegios de root)
- Los volúmenes se montan en tiempo de ejecución (config, reglas, scripts)

---

### 7. `deploy.sh` - Script de Despliegue

**Funciones:**

1. **Construye la imagen Docker personalizada**
   ```bash
   docker build -t elastalert2-custom /home/debian/elastalert/docker
   ```

2. **Despliega el contenedor ElastAlert2** conectado a la red T-Pot
   - Monta volúmenes para: configuración, reglas, scripts
   - Se conecta a la red `tpotce_nginx_local` para comunicarse con Elasticsearch
   - Ejecuta en modo daemon con logs verbosos

**Volúmenes montados:**
- `/opt/elastalert/config.yaml` ← Configuración
- `/opt/elastalert/rules/` ← Reglas de detección
- `/opt/elastalert/scripts/` ← Scripts de integración con TheHive

---

## 🔄 Flujo Completo de Automatización

```
1. ATAQUE → T-Pot (Cowrie) detecta intento de login
                    ↓
2. REGISTRO → Elasticsearch almacena el evento (logstash-*)
                    ↓
3. ESCANEO → ElastAlert2 busca eventos cada minuto
                    ↓
4. COINCIDENCIA → cowrie.yaml detecta el evento
                    ↓
5. ALERTA → alerta_cowrie_login.py crea alerta en TheHive
                    ↓
6. AGREGACIÓN → caso_cowrie_login.py agrupa alertas de 24h
                    ↓
7. CASO → Se crea caso diario con estadísticas consolidadas
                    ↓
8. ANÁLISIS → Usuario "Zeroday" revisa el caso en TheHive
```

---

### Configuración de Crontab

Para ejecutar automáticamente el script de análisis de Cowrie cada 10 minutos (útil para pruebas), se puede configurar una tarea en crontab:

1. **Abrir el editor de crontab:**
    ```bash
    crontab -e
    ```

2. **Añadir la siguiente línea:**
    ```bash
    */10 * * * * /usr/bin/python3 /home/debian/elastalert/scripts/caso_cowrie_login.py
    ```

3. **Guardar y salir** (en nano: `Ctrl+O`, `Enter`, `Ctrl+X`).

**Nota:** Esta configuración ejecuta el script cada 10 minutos. Para cambiar la frecuencia a cada 24 horas (configuración recomendada en producción), utiliza:
```bash
0 0 * * * /usr/bin/python3 /home/debian/elastalert/scripts/caso_cowrie_login.py
```

---

### Código del Proyecto

Este repositorio contiene los archivos de configuración clave utilizados para la implementación:

* [`src/elastalert/rules/cowrie.yaml`](#) (Regla de ElastAlert2 para el honeypot Cowrie)
* [`src/elastalert/config/config.yaml`](#) (Configuración principal de ElastAlert2)
* [`src/elastalert/docker/Dockerfile`](#) (Dockerfile para el despliegue de ElastAlert2)
* [`src/elastalert/docker/deploy.sh`](#) (Script de despliegue para ElastAlert2)
* [`src/elastalert/docker/prune.sh`](#) (Script para limpieza de contenedores)
* [`src/elastalert/scripts/alerta_cowrie_login.py`](#) (Script para crear alertas en TheHive)
* [`src/elastalert/scripts/caso_cowrie_login.py`](#) (Script para crear casos en TheHive)
* [`src/elastalert/scripts/thehive_methods.py`](#) (Módulo con métodos para interactuar con TheHive)

---

## 👥 Autores

Este proyecto fue desarrollado por el equipo **zeroday** durante el Hackathon de Ciberseguridad de la Universidad de Zaragoza:

- **Emilliano Recuenco López**
- **José Miguel Quílez Vergara**
- **Jorge Lucas Ferrer**
- **Curro Valero Casajús** 

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [`LICENSE`](LICENSE) para más detalles.
