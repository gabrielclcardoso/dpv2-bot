import json
import query

API_ENDPOINT = 'https://explorer.nymtech.net/api/v1/mix-node/'

with open('../data/database.json', 'r') as const_file:
    database = json.load(const_file)


def update_node(mix_id):
    response = query.query_api(mix_id)
    mixnode = database[mix_id]
    mixnode['location']['country_name'] = response['location']['country_name']
    mixnode['mix_node']['host'] = response['mix_node']['host']
    mixnode['operating_cost']['amount'] = response['operating_cost']['amount']
    mixnode['profit_margin_percent'] = response['profit_margin_percent']
    database[mix_id] = mixnode
    with open('../data/database.json', 'w') as mod_file:
        mod_file.write(json.dumps(database))
