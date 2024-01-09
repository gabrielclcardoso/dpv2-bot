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
    if not os.path.exists('../data/database.json'):
        open("../data/database.json", 'x')
    if os.stat("../data/database.json").st_size == 0:
        database = json.loads('{}')
    else:
        with open("../data/database.json", 'r+') as data:
            database = json.load(data)
    file = open("../data/database.json", 'w')
except FileNotFoundError:
    sys.stderr.write(
        "Error: Unable to create file '../data/database.json'\n")
    exit(1)

# Filling databse
for i in range(1, sys.argv.__len__()):
    if sys.argv[i] in database:
        print("Mixnode " + sys.argv[i] + " already on the database")
        continue
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
    database[mixnode['mix_id']] = mixnode
    print(str(i) + '/' + str(sys.argv.__len__() - 1))
file.write(json.dumps(database))
