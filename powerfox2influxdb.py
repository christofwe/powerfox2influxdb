import json
import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

import time
from datetime import datetime

from influxdb import InfluxDBClient

INFLUXDB_HOST = os.environ['INFLUXDB_HOST']
INFLUXDB_PORT = os.environ['INFLUXDB_PORT']
INFLUXDB_USER = os.environ['INFLUXDB_USER']
INFLUXDB_PASS = os.environ['INFLUXDB_PASS']
INFLUXDB_DB_NAME = os.environ['INFLUXDB_DB_NAME']

POWERFOX_API = os.environ['POWERFOX_API']
POWERFOX_USER = os.environ['POWERFOX_USER']
POWERFOX_PASSWORD = os.environ['POWERFOX_PASSWORD']

# POWERFOX_API=https://backend.powerfox.energy/api/2.0/my/main

influx_client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, username=INFLUXDB_USER, password=INFLUXDB_PASS)
influx_client.switch_database(INFLUXDB_DB_NAME)

local = datetime.now()
timestamp = local.strftime("%Y-%m-%dT%H:%M:%SZ")

powerfox_headers = {'Content-Type': 'application/json'}
powerfox_params = {'unit': 'kwh'}

powerfox_response_current = requests.get(f"{POWERFOX_API}/current", params=powerfox_params, headers=powerfox_headers, auth=(POWERFOX_USER, POWERFOX_PASSWORD), verify=False)

print(f"{timestamp} powerfox_response_current: {powerfox_response_current}")