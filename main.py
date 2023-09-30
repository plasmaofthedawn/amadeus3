import json

import amadeus

with open('data/config.json') as json_data_file:
    data = json.load(json_data_file)
    token = data['discord']['token']

client = amadeus.create_client()
client.run(token)
