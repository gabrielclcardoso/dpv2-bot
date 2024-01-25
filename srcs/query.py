import json
import requests
import sys

API_ENDPOINT = 'https://explorer.nymtech.net/api/v1/mix-node/'


def outdated_version(version, current):
    if not version:
        return False
    version_arr = version.split('.')
    current_arr = current.split('.')
    if len(current_arr) != 3:
        return True
    current_nbr = int(current_arr[len(current_arr) - 1])
    version_nbr = int(version_arr[len(version_arr) - 1])
    if version_nbr - current_nbr > 2 or version_nbr - current_nbr < -1:
        return True
    else:
        return False


def query_api(mix_id):
    try:
        response = requests.get(API_ENDPOINT + mix_id)
    except requests.exceptions.ConnectionError:
        sys.stderr.write('Error: Unable to reach -> ' +
                         API_ENDPOINT + mix_id + '\n')
        raise
    if response.status_code != 200:
        sys.stderr.write('Error: Got response ' + str(response.status_code) +
                         ' on ' + API_ENDPOINT + mix_id + '\n')
        raise (ValueError)
    return json.loads(response.content)


def compare_info(database, current, version):
    changed_parameters = []
    initial = database[str(current['mix_id'])]
    if current['location']['country_name'] != initial['location']['country_name']:
        changed_parameters.append('location')
    if current['mix_node']['host'] != initial['mix_node']['host']:
        changed_parameters.append('host')
    if current['operating_cost']['amount'] != initial['operating_cost']['amount']:
        changed_parameters.append('operating_cost')
    if current['profit_margin_percent'] != initial['profit_margin_percent']:
        changed_parameters.append('profit_margin')
    if current['stake_saturation'] > 0.95:
        changed_parameters.append('saturation')
    if current['avg_uptime'] < 70:
        changed_parameters.append('uptime')
    if outdated_version(version, current['mix_node']['version']):
        changed_parameters.append('version')

    return changed_parameters


def message(database, current, warnings):
    initial = database[str(current['mix_id'])]
    message = ('Warnings for mixnode ' +
               str(current['mix_id']) + ' | ' +
               current['mix_node']['identity_key'] + '\n\n')
    if 'location' in warnings:
        message += ('🌐 Location changed from ' +
                    initial['location']['country_name'] + ' to ' +
                    current['location']['country_name'] + '\n')
    if 'host' in warnings:
        message += ('🌐 Host changed from ' + initial['mix_node']['host'] +
                    ' to ' + current['mix_node']['host'] + '\n')
    if 'operating_cost' in warnings:
        message += ('💰 Operating cost changed from ' +
                    str(int(initial['operating_cost']['amount']) / 1000000) +
                    ' to ' + str(int(current['operating_cost']['amount']) /
                                 1000000) + '\n')
    if 'profit_margin' in warnings:
        message += ('💰 Profit margin changed from ' +
                    initial['profit_margin_percent'] + ' to ' +
                    current['profit_margin_percent'] + '\n')
    if 'saturation' in warnings:
        message += ('✅ Saturation reached ' + str(current['stake_saturation'])
                    + ' surpassing the 95% mark\n')
    if 'uptime' in warnings:
        message += (
            '❌ Node is having a bad performance with an average routing ' +
            'score of ' + str(current['avg_uptime']) +
            '% which is below 70%\n')
    if 'version' in warnings:
        message += ('❌ Node is running on an outdated version, the version ' +
                    'being ran by the node is ' +
                    f'{current["mix_node"]["version"]}\n')
    return message
