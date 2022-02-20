import os

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from datetime import datetime, timedelta
import pytz

from influxdb import InfluxDBClient

INFLUXDB_HOST = os.environ['INFLUXDB_HOST']
INFLUXDB_PORT = os.environ['INFLUXDB_PORT']
INFLUXDB_USER = os.environ['INFLUXDB_USER']
INFLUXDB_PASS = os.environ['INFLUXDB_PASS']
INFLUXDB_DB_NAME = os.environ['INFLUXDB_DB_NAME']

POWERFOX_REPORT_YEAR = os.environ['POWERFOX_REPORT_YEAR']
POWERFOX_API = os.environ['POWERFOX_API']
POWERFOX_USER = os.environ['POWERFOX_USER']
POWERFOX_PASSWORD = os.environ['POWERFOX_PASSWORD']


tz = pytz.timezone(os.environ['TZ'])
local = tz.localize(datetime.now())
timestamp = local.strftime("%Y-%m-%dT%H:%M:%S%Z%z")

influx_client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, username=INFLUXDB_USER, password=INFLUXDB_PASS)
influx_client.switch_database(INFLUXDB_DB_NAME)
influx_body = []

powerfox_headers = {'Content-Type': 'application/json'}
powerfox_current_params = {"unit": "kwh"}
powerfox_report_params = {"year": POWERFOX_REPORT_YEAR}

values_current_kwh = ["A_Plus","A_Minus"]
values_current_watt = ["Watt"]
values_report_kwh = ["Consumption", "FeedIn"]


try:
  powerfox_current_response = requests.get(f"{POWERFOX_API}/main/current", headers=powerfox_headers, auth=(POWERFOX_USER, POWERFOX_PASSWORD), verify=False, params=powerfox_current_params)
  powerfox_current_response.raise_for_status()
  powerfox_current = powerfox_current_response.json()
  timestamp_current = tz.localize(datetime.utcfromtimestamp(powerfox_current['Timestamp']))

  for value in values_current_kwh:
    item = {
      "measurement": value,
      "tags": {
        "type": "current"
      },
      "time": timestamp_current.isoformat(),
      "fields": {
        "kwh": powerfox_current[value]
      }
    }
    influx_body.append(item)

  for value in values_current_watt:
    item = {
      "measurement": value,
      "tags": {
        "type": "current"
      },
      "time": timestamp_current.isoformat(),
      "fields": {
        "watts": powerfox_current[value]
      }
    }
    influx_body.append(item)

  if local.day == 1 and local.hour == 6 and local.minute < 5:
    powerfox_report_response = requests.get(f"{POWERFOX_API}/all/report", headers=powerfox_headers, auth=(POWERFOX_USER, POWERFOX_PASSWORD), verify=False, params=powerfox_report_params)
    powerfox_report_response.raise_for_status()
    powerfox_report = powerfox_report_response.json()

    for value in values_report_kwh:
      for rv in powerfox_report[value]['ReportValues']:
        timestamp_rv = tz.localize(datetime.utcfromtimestamp(rv['Timestamp']))
        item = {
          "measurement": value,
          "tags": {
            "type": "report"
          },
          "time": timestamp_rv.isoformat(),
          "fields": {
            "kwh": rv['Delta'],
            "month": datetime.utcfromtimestamp(rv['Timestamp']).month,
            "year": datetime.utcfromtimestamp(rv['Timestamp']).year
          }
        }
        influx_body.append(item)


  influxdb_write = influx_client.write_points(influx_body)
  print(f"{timestamp} influxdb_write: {influxdb_write}")

except requests.exceptions.HTTPError as error:
  print(f"powerfox_current error: {error}")
  print(f"powerfox_current status_code: {powerfox_current_response.status_code}")
