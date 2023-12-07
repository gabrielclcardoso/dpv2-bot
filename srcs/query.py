import json
import requests
import sys

API_ENDPOINT = 'https://explorer.nymtech.net/api/v1/mix-node/'

with open('../data/database.json') as file:
    database = json.load(file)['mixnodes']


def query_api(mix_id):
    try:
        response = requests.get(API_ENDPOINT + mix_id)
    except requests.exceptions.ConnectionError:
        sys.stderr.write('Error: Unable to reach -> ' +
                         API_ENDPOINT + mix_id + '\n')
    if response.status_code != 200:
        sys.stderr.write('Error: Got response ' + str(response.status_code) +
                         ' on ' + API_ENDPOINT + mix_id + '\n')
        raise (ValueError)
    return json.loads(response.content)


def compare_info(current):
    changed_parameters = []
    initial = database[mix_id]
    try:
        current = query_api(mix_id)
    except ValueError:
        return changed_parameters.append('fail')
    if current['location']['country_name'] != initial['location']['country_name']:
        changed_parameters.append('location')
    if current['mix_node']['host'] != initial['mix_node']['host']:
        changed_parameters.append('host')
    if current['operating_cost']['amount'] != initial['operating_cost']['amount']:
        changed_parameters.append('operating_cost')
    if current['profit_margin_percent'] != initial['profit_margin_percent']:
        changed_parameters.append('profit_margin')
    if current['stake_saturation'] > 0.7:
        changed_parameters.append('saturation')
    if current['avg_uptime'] < 50:
        changed_parameters.append('uptime')
    return changed_parameters


def send_warnings(current, warnings):
    initial = database[mix_id]
    message = 'Warnings for mixnode ' + str(current['mix_id']) + ' | ' + \
        current['mix_node']['identity_key'] + '\n'
    if 'location' in warnings:
        message += \
            ('🌐 Location changed from ' + initial['location']['country_name']
             + ' to ' + current['location']['country_name'] + '\n')
    if 'host' in warnings:
        message += \
            ('🌐 Host changed from ' + initial['mix_node']['host'] + ' to ' +
             current['mix_node']['host'] + '\n')
    if 'operating_cost' in warnings:
        message += \
            ('💰 Operating cost changed from ' +
             str(int(initial['operating_cost']['amount']) / 1000000) + ' to ' +
             str(int(current['operating_cost']['amount']) / 1000000) + '\n')
    if 'profit_margin' in warnings:
        message += \
            ('💰 Profit margin changed from ' +
             initial['profit_margin_percent'] + ' to ' +
             current['profit_margin_percent'] + '\n')
    if 'saturation' in warnings:
        message += \
            ('✅ Saturation reached ' + str(current['stake_saturation']) +
             ' surpassing the 70% mark\n')
    if 'uptime' in warnings:
        message += (
            '❌ Node is having a bad performance with an average routing ' +
            'score of ' + str(current['avg_uptime']) +
            '% which is below 50%\n')
    print(message)


for mix_id in database:
    try:
        current = query_api(mix_id)
    except ValueError:
        sys.stderr.write('Error fetching info for node ' + mix_id)
        continue
    warnings = compare_info(mix_id)
    if warnings.__len__() == 0:
        continue
    else:
        send_warnings(current, warnings)
