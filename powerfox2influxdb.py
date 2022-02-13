import json
import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

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
# powerfox_params = {'unit': 'kwh'}

# powerfox_current = requests.get(f"{POWERFOX_API}/current", params=powerfox_params, headers=powerfox_headers, auth=(POWERFOX_USER, POWERFOX_PASSWORD), verify=False)
try:
  powerfox_current_response = requests.get(f"{POWERFOX_API}/current", headers=powerfox_headers, auth=(POWERFOX_USER, POWERFOX_PASSWORD), verify=False)

  powerfox_current_response.raise_for_status()

  powerfox_current = json.loads(powerfox_current_response.text)


  values_current_watts = ["A_Plus","A_Minus", "Watt"]

  json_body = []
  for value_current_watt in values_current_watts:
    item = {
      "measurement": value_current_watt,
      "tags": {
      },
      "time": datetime.utcfromtimestamp(powerfox_current['Timestamp']).strftime("%Y-%m-%dT%H:%M:%SZ"),
      "fields": {
        "watts": powerfox_current[value_current_watt]
      }
    }
    json_body.append(item)


  influxdb_write = influx_client.write_points(json_body)
  print(f"{timestamp} influx_write: {influxdb_write}")

except requests.exceptions.HTTPError as error:
  print(f"powerfox_current error: {error}")
  print(f"powerfox_current status_code: {powerfox_current_response.status_code}")
