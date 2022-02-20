# powerfox2influxdb

Simple container that queries powerfox's(https://www.powerfox.energy) API and writes metrics to a (local) influxDB.

## Requirements:
- Docker execution runtime
- powerfox account/

## Steps
1. Copy `.env.sample` to `.env` and update w/ actual values
2. Run `docker-compose up -d`