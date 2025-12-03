import datetime 
import requests
import json
import time

# Configuracion de TheHive
thehive_url = 'URL_DE_TU_THEHIVE'
thehive_api_key = 'API_KEY_DE_TU_THEHIVE'

def crear_alerta(alert_data, max_retries=3, retry_delay=5):
    url = f"{thehive_url}/api/v1/alert"
    headers = {
        "Authorization": f"Bearer {thehive_api_key}",
        "Content-Type": "application/json"
    }

    for intento in range(1, max_retries + 1):
        try:
            response = requests.post(url, headers=headers, json=alert_data, verify=False)

            if response.status_code == 201:
                print(f"[SUCCESS {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Alerta creada exitosamente.")
                return response.json()
            else:
                print(f"[ERROR {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error al crear la alerta (intento {intento}): {response.status_code}")
                print(f"[DETAILS {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Detalles del error: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"[CONNECTION {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error de conexión en el intento {intento}: {e}")

        if intento < max_retries:
            print(f"[RETRY {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Reintentando en {retry_delay} segundos...\n")
            time.sleep(retry_delay)
        else:
            print(f"[MAX_RETRIES {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Se alcanzó el número máximo de reintentos.")

    return None

def crear_caso(titulo, descripcion, observables, severity, tags, status):
    url = f"{thehive_url}/api/case"
    headers = {
        "Authorization": f"Bearer {thehive_api_key}",
        "Content-Type": "application/json"
    }

    # Cuerpo del caso que se va a crear
    caso_data = {
        "title": titulo,
        "description": descripcion,
        "observables": observables,
        "severity": severity,  # Puedes ajustar la severidad según tus necesidades
        "tags": tags,  # Etiquetas opcionales, puedes agregar más si lo deseas
        "status": status,  # Estado inicial del caso
    }

    try:
        response = requests.post(url, headers=headers, json=caso_data, verify=False)
        if response.status_code == 201:
            print(f"[CASE_CREATED {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Caso creado exitosamente.")
            return response.json()  # Devuelve el caso creado
        else:
            print(f"[CASE_ERROR {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error al crear el caso: {response.status_code}")
            print(f"[DETAILS {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Detalles del error: {response.text}")
            return None
    except Exception as e:
        print(f"[CONNECTION {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error de conexión: {e}")
        return None

def vincular_caso_a_alerta(caso_id, alerta_id):
    url = f"{thehive_url}/api/v1/alert/{alerta_id}/merge/{caso_id}"
    headers = {
        "Authorization": f"Bearer {thehive_api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, verify=False)
        if response.status_code == 200:
            print(f"[LINK_SUCCESS {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Caso vinculado a la alerta exitosamente.")
            return response.json()  # Devuelve la información del caso vinculado
        else:
            print(f"[LINK_ERROR {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error al vincular el caso a la alerta: {response.status_code}")
            print(f"[DETAILS {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Detalles del error: {response.text}")
            return None
    except Exception as e:
        print(f"[CONNECTION {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error de conexión: {e}")
        return None

def crear_caso_cowrie_24h():
    """
    Crea un único caso en TheHive con todas las alertas de Cowrie de las últimas 24 horas.
    """
    # Calculamos el timestamp de hace 24 horas
    timestamp_24h_antes = int((time.time() - 86400) * 1000)  # milisegundos
    
    # URL para buscar alertas de Cowrie
    url = f"{thehive_url}/api/alert/_search?range=0-1000"
    headers = {
        "Authorization": f"Bearer {thehive_api_key}",
        "Content-Type": "application/json"
    }
    
    # Consulta para obtener alertas de Cowrie de las últimas 24 horas
    query = {
        "query": {
            "_and": [
                {
                    "_field": "tags",
                    "_value": "cowrie",
                },
                {
                    "_field": "status",
                    "_value": "New",
                },                
                {
                    "_gt": { "createdAt": timestamp_24h_antes }
                }
            ]
        },
        "sort": ["-createdAt"]
    }
    
    try:
        # Obtenemos las alertas
        response = requests.post(url, headers=headers, json=query, verify=False)
        
        if response.status_code != 200:
            print(f"[SEARCH_ERROR {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error al buscar alertas: {response.status_code}")
            print(f"[DETAILS {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Detalles del error: {response.text}")
            return False
        
        alertas = response.json()
        
        if not alertas:
            print(f"[NO_ALERTS {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No se encontraron alertas de Cowrie en las últimas 24 horas.")
            return True
        
        print(f"[STATS {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Se encontraron {len(alertas)} alertas de Cowrie en las últimas 24 horas.")
        
        # Variables para el caso único
        todas_ips = set()
        todos_paises = set()
        todas_regiones = set()
        todos_usuarios = set()
        todos_asns = set()
        timestamps = []
        
        # Procesamos todas las alertas
        for alerta in alertas:
            try:
                # Extraemos información del título
                title_parts = alerta['title'].split(' - ')
                if len(title_parts) >= 4:
                    user = title_parts[1]
                    remip = title_parts[2]
                    as_org = title_parts[3]
                    
                    todos_usuarios.add(user)
                    todas_ips.add(remip)
                    todos_asns.add(as_org)
                    
                    # Extraemos información adicional
                    desc_lines = alerta['description'].split('\n')
                    country = next((line.split(': ')[1] for line in desc_lines if line.startswith('Pais:')), "Desconocido")
                    region = next((line.split(': ')[1] for line in desc_lines if line.startswith('Region:')), "Desconocido")
                    
                    todos_paises.add(country)
                    todas_regiones.add(region)
                    timestamps.append(alerta['createdAt'])
                
            except Exception as e:
                print(f"[PROCESS_ERROR {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error al procesar alerta {alerta.get('id', 'unknown')}: {e}")
                continue
        
        # Creamos un ÚNICO caso con todas las alertas
        fecha_hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        titulo = f"Resumen de Login de Cowrie - {fecha_hora_actual}"
        
        primer_timestamp = min(timestamps) if timestamps else 0
        ultimo_timestamp = max(timestamps) if timestamps else 0
        
        descripcion = (
            f"Resumen diario de actividad en honeypot Cowrie (últimas 24h):\n\n"
            f"**Estadísticas generales:**\n"
            f"- Total eventos: {len(alertas)}\n"
            f"- IPs únicas: {len(todas_ips)}\n"
            f"- Usuarios atacados: {len(todos_usuarios)}\n"
            f"- ASNs/organizaciones: {len(todos_asns)}\n"
            f"- Países: {', '.join(todos_paises)}\n"
            f"- Regiones: {', '.join(todas_regiones)}\n\n"
            f"**Rango temporal:**\n"
            f"- Primer evento: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(primer_timestamp/1000))}\n"
            f"- Último evento: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ultimo_timestamp/1000))}\n\n"
            f"**Detalles de IPs:**\n" + "\n".join(f"- {ip}" for ip in todas_ips)
        )
        
        # Observables para el caso
        observables = []
        for ip in todas_ips:
            observables.append({
                "dataType": "ip",
                "data": ip,
                "ioc": True,
                "message": f"IP atacante: {ip}"
            })
        
        for user in todos_usuarios:
            observables.append({
                "dataType": "user",
                "data": user,
                "ioc": True,
                "message": f"Usuario objetivo: {user}"
            })
        
        for as_org in todos_asns:
            observables.append({
                "dataType": "autonomous-system",
                "data": as_org,
                "ioc": True,
                "message": f"ASN/Organización: {as_org}"
            })
        
        for region in todas_regiones:
            if region != "Desconocido":
                observables.append({
                    "dataType": "location",
                    "data": region,
                    "ioc": True,
                    "message": f"Región origen: {region}"
            })

        for pais in todos_paises:
            if pais != "Desconocido":
                observables.append({
                    "dataType": "location",
                    "data": pais,
                    "ioc": True,
                    "message": f"País origen: {pais}"
            })

        severity = 2  # Medium severity
        tags = ["cowrie", "honeypot", "brute-force", "ssh", "daily-report"]
        status = "New"
        
        # Intentamos crear el caso indefinidamente si falla
        while True:
            try:
                caso = crear_caso(titulo, descripcion, observables, severity, tags, status)
                if caso:
                    caso_id = caso['id']
                    # Vinculamos TODAS las alertas al caso
                    for alerta in alertas:
                        alerta_id = alerta['id']
                        vincular_caso_a_alerta(caso_id, alerta_id)
                    
                    print(f"[CASE_LINKED {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Creado caso único con {len(alertas)} alertas de Cowrie vinculadas")
                    break  # salimos del bucle si se creó correctamente
                else:
                    print(f"[CASE_FAILURE {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Fallo al crear el caso, reintentando en 5 segundos...")
            except Exception as e:
                print(f"[EXCEPTION {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Excepción al crear el caso: {e}, reintentando en 5 segundos...")
            
            time.sleep(5)

    
    except Exception as e:
        print(f"[GENERAL_ERROR {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error al procesar alertas de Cowrie: {e}")
        return False
