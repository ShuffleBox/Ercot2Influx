#!/usr/bin/env python
'''
ercot current grid status importer
'''
import argparse
from datetime import datetime
import pytz
import requests
from influxdb import InfluxDBClient
from bs4 import BeautifulSoup

def main(args):
    '''
    * Get Ercot status page
    * parse table contents to build payload
    * initialize InfluxDB client
    * commit payload
    '''
    payload_dict = {}
    ercot_request = requests.get('http://www.ercot.com/content/cdr/html/real_time_system_conditions.html')
    soup_results = BeautifulSoup(ercot_request.text, 'html.parser')
    table_contents = soup_results.find('table')
    rows = table_contents.find_all("tr")

    for tr in rows:
        row = tr.find_all("td")
        if len(row) == 2:
            title = row[0].get_text()
            data = float(row[1].get_text())
            payload_dict[title] = data

    #make influxDB client
    influx_client = InfluxDBClient(args.influx_server,
                                args.influx_port,
                                args.influx_user,
                                args.influx_password,
                                args.influx_database)

    payload = {}
    payload['measurement'] = 'Ercot Real-Time System Conditions'
    payload['fields'] = payload_dict
    commit = []
    commit.append(payload)
    influx_client.write_points(commit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ercot status page to InfluxDB logger')
    parser.add_argument('-s','--influx-server',help='InfluxDB host', required=True)
    parser.add_argument('-o','--influx-port',default=8086,help='InfluxDB Port', required=False)
    parser.add_argument('-u','--influx-user',help='InfluxDB username', required=True)
    parser.add_argument('-p','--influx-password',help='InfluxDB password', required=True)
    parser.add_argument('-d','--influx-database',help='InfluxDB BikeCounter DB name', required=False)

    args = parser.parse_args()
    main(args)
