import os

import requests
from requests.auth import HTTPBasicAuth
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

POWERFOX_API = os.environ['POWERFOX_API']
POWERFOX_USER = os.environ['POWERFOX_USER']
POWERFOX_PASSWORD = os.environ['POWERFOX_PASSWORD']
POWERFOX_DEVICE_ID = os.environ['POWERFOX_DEVICE_ID']


tz = pytz.timezone(os.environ['TZ'])
local = tz.localize(datetime.now())
timestamp = local.strftime("%Y-%m-%dT%H:%M:%S%Z%z")

influx_client = InfluxDBClient(host=INFLUXDB_HOST, port=INFLUXDB_PORT, username=INFLUXDB_USER, password=INFLUXDB_PASS)
influx_client.switch_database(INFLUXDB_DB_NAME)
influx_body = []

def set_params(local, period="MONTH"):
  params = {
    'year': local.year
  }
  if period == "DAY":
    params.update({
    'month': local.month
    })
  return params

def get_report(params):
  powerfox_auth = HTTPBasicAuth(POWERFOX_USER, POWERFOX_PASSWORD)
  powerfox_headers = {'Content-Type': 'application/json'}
  report = requests.get(f"{POWERFOX_API}/my/{POWERFOX_DEVICE_ID}/report", headers=powerfox_headers, auth=powerfox_auth, verify=False, params=params)
  report.raise_for_status()
  return report.json()

def generate_data_points(report, period="MONTH"):
  data_points = []
  report_objects = ["Consumption", "FeedIn"]
  for object in report_objects:
    for value in report[object]['ReportValues']:
      timestamp = tz.localize(datetime.fromtimestamp(value['Timestamp']))
      point = {
        "measurement": f"{object}_{period}",
        "tags": {
          "type": "report",
          "period": period,
        },
        "time": timestamp.isoformat(),
        "fields": {
          "kwh": value['Delta']
        }
      }
      data_points.append(point)
  return data_points

influx_body.extend(generate_data_points(get_report(set_params(local))))
influx_body.extend(generate_data_points(get_report(set_params(local, "DAY")), "DAY"))

print(influx_body)

if influx_body:
  influxdb_write = influx_client.write_points(influx_body)
  print(f"{timestamp} influxdb_write: {influxdb_write}")
else:
  print(f"{timestamp} influxdb_write: no")
