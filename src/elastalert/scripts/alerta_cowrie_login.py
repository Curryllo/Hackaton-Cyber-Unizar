import argparse
import time
import thehive_methods

def main():
    # Creamos el parser para argumentos de linea de comandos
    parser = argparse.ArgumentParser(description='Procesar alerta de login exitoso (cowrie).')
    parser.add_argument('--user', required=False, help='user')
    parser.add_argument('--remip', required=False, help='ip')
    parser.add_argument('--as_org', required=False, help='ASN')
    parser.add_argument('--country', required=False, help='pais')
    parser.add_argument('--region', required=False, help='region')
    parser.add_argument('--timestamp', required=False, help='timestamp')

    # Parseamos los argumentos recibidos
    args = parser.parse_args()
    user = args.user
    remip = args.remip
    as_org = args.as_org
    country = args.country
    region = args.region
    timestamp = args.timestamp

    # Creamos un identificador unico para la alerta usando el timestamp actual
    source_ref = f"cowrie_login_{int(time.time())}"

    # Construimos los datos de la alerta en formato diccionario
    alert_data = {
        "type": "external",
        "source": "elastalert-logstash",
        "sourceRef": source_ref,
        "title": f"Cowrie login - {user} - {remip} - {as_org}",
        "description": f"Se detecto un login en el honeypot Cowrie.\n"
                       f"Fecha: {timestamp}\n"
                       f"IP: {remip}\n"
                       f"Pais: {country}\n"
                       f"Region: {region}",
        "severity": 2,
        "tags": ["cowrie", "elastalert"],
        "observables": [
            {
                "dataType": "account",
                "data": user,
                "ioc": True
            },
            {
                "dataType": "ip",
                "data": remip,
                "ioc": True
            },
            {
                "dataType": "autonomous-system",
                "data": as_org,
                "ioc": True
            },
            {
                "dataType": "region",
                "data": region,
                "ioc": True
            }
        ]
    }

    # Llamamos al metodo para crear la alerta en TheHive
    alerta = thehive_methods.crear_alerta(alert_data)

if __name__ == "__main__":
    main()
