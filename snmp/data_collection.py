from pysnmp.hlapi import *
import pandas as pd
import time
from datetime import datetime

# OIDs para CPU, memoria y disco
OIDS = {
    'cpu_usage': '1.3.6.1.4.1.2021.11.9.0',
    'total_memory': '1.3.6.1.4.1.2021.4.5.0',
    'free_memory': '1.3.6.1.4.1.2021.4.6.0',
    'total_disk': '1.3.6.1.4.1.2021.9.1.6.1',
    'available_disk': '1.3.6.1.4.1.2021.9.1.7.1'
}

# Función para consultar un OID específico
def snmp_get(oid):
    iterator = getCmd(SnmpEngine(),
                      CommunityData('public', mpModel=0), # Cambiar 'public' si tu comunidad es diferente
                      UdpTransportTarget(('192.168.56.1', 161)),
                      ContextData(),
                      ObjectType(ObjectIdentity(oid)))
    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
    
    if errorIndication:
        print(errorIndication)
        return None
    elif errorStatus:
        print('%s at %s' % (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        return None
    else:
        for varBind in varBinds:
            return int(varBind[1])  # Convertir el valor a entero

# Recolección de datos en intervalos regulares
def collect_data(interval_minutes=15, duration_days=3):
    data = []
    end_time = time.time() + duration_days * 24 * 60 * 60  # Duración en segundos

    while time.time() < end_time:
        timestamp = datetime.now()
        row = {
            'timestamp': timestamp,
            'cpu_usage': snmp_get(OIDS['cpu_usage']),
            'total_memory': snmp_get(OIDS['total_memory']),
            'free_memory': snmp_get(OIDS['free_memory']),
            'total_disk': snmp_get(OIDS['total_disk']),
            'available_disk': snmp_get(OIDS['available_disk']),
        }
        data.append(row)
        
        # Guardar los datos en un CSV cada vez que se recolecta
        df = pd.DataFrame(data)
        df.to_csv('monitoring_data.csv', index=False)
        
        print(f"Datos recolectados a las {timestamp}: {row}")
        
        time.sleep(interval_minutes * 60)  # Esperar el intervalo en segundos

# Iniciar la recolección de datos con un intervalo de 15 minutos por 3 días
collect_data(interval_minutes=15, duration_days=3)
