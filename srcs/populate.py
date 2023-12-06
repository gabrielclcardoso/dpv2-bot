import os
import sys
import json
import requests

API_ENDPOINT = "https://explorer.nymtech.net/api/v1/mix-node/"

# Argument checking
if sys.argv.__len__() <= 1:
    sys.stderr.write("Error: No mix-ids given to populate database\n")
    exit(1)

# File checking
try:
    if os.stat("../data/database.json").st_size != 0:
        sys.stderr.write("Error: Database already populated\n")
        exit(1)
except FileNotFoundError:
    try:
        file = open("../data/database.json", 'x')
    except FileNotFoundError:
        sys.stderr.write(
            "Error: Unable to create file '../data/database.json'\n")
        exit(1)

# Filling databse
database = json.loads('{"mixnodes": {}}')
for i in range(1, sys.argv.__len__()):
    try:
        response = requests.get(API_ENDPOINT + sys.argv[i])
    except requests.exceptions.ConnectionError:
        sys.stderr.write("Error: Unable to reach -> " +
                         API_ENDPOINT + sys.argv[i] + '\n')
        continue
    if response.status_code != 200:
        sys.stderr.write("Error: Got response " + str(response.status_code) +
                         " on " + API_ENDPOINT + sys.argv[i] + '\n')
        continue
    mixnode = json.loads(response.content)
    database['mixnodes'][mixnode['mix_id']] = mixnode
    print(str(i) + '/' + str(sys.argv.__len__() - 1))
file.write(json.dumps(database))
