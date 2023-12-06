import os
import sys
import json

# Argument checking
if sys.argv.__len__() <= 1:
    sys.stderr.write("No mix-ids given to populate database\n")
    exit(1)

# File checking
try:
    if os.stat("../data/database.json").st_size != 0:
        sys.stderr.write("Database already populated\n")
        exit(1)
except FileNotFoundError:
    try:
        file = open("../data/database.json", 'x')
    except FileNotFoundError:
        sys.stderr.write("Unable to create file '../data/database.json'\n")
        exit(1)

database = json.loads('{"nodes": {}}')

for i in range(1, sys.argv.__len__()):
    print(sys.argv[i])
