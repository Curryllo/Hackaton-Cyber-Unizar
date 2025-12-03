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
* **Comando de Despliegue:**
    ```bash
    docker pull strangebee/thehive:5.4.6-1
    sudo docker run -d --name thehive \
    -p 9000:9000 \
    strangebee/thehive:5.4.6-1
    ```
* **Hardware:** Lenovo (8GB RAM, 1TB Almacenamiento, 4 Cores).
* **Acceso Inicial:** `https://thehive.eslus.org` (Puerto interno `9000`).
* **Usuario de Análisis:** Se creó la organización y el usuario **`Zeroday`** para gestionar los casos y alertas.

### 2. Despliegue de T-Pot (Plataforma de Honeypot)

T-Pot se instaló en una máquina virtual dedicada con los recursos necesarios para orquestar múltiples honeypots.

* **Plataforma Host:** N100 (16GB RAM, 526GB Almacenamiento, 4 Cores) bajo OpenNebula.
* **VM (Debian 12) Requisitos:** 8GB RAM, 254GB Espacio, 4 CPUs.
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
* **URL de Acceso:** `https://tpot.eslus.org`

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

## 🚀 Uso del Sistema

El sistema opera de forma continua, ejecutando el ciclo de vida del incidente de forma automática:

1.  **Ataque:** Un actor malicioso interactúa con un servicio del honeypot de T-Pot (ej. intenta login en Cowrie).
2.  **Detección y Recolección:** T-Pot registra el evento en su *Elasticsearch*.
3.  **Alerta (ElastAlert2):** ElastAlert2 detecta el nuevo log en Cowrie y dispara un *script* que usa la API de TheHive.
4.  **Creación de Casos/Alertas (TheHive):** Se crea automáticamente un nuevo Caso y/o Alerta en TheHive.
5.  **Análisis (Usuario Zeroday):** El analista (**Zeroday**) accede a TheHive, revisa el Caso creado, enriquece la información y ejecuta las acciones de respuesta (cerrar, escalar, investigar, etc.).

Este flujo asegura que el analista no tenga que pasar tiempo buscando actividad sospechosa, sino que se concentre únicamente en la **investigación y respuesta** de los incidentes ya clasificados.

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

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo [`LICENSE`](LICENSE) para más detalles.
