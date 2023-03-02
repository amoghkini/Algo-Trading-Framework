import json
import os

def get_server_config():
  with open('../config/server.json', 'r') as server:
    json_server_data = json.load(server)
    return json_server_data


def get_system_config():
  with open('../config/system.json', 'r') as system:
    json_system_data = json.load(system)
    return json_system_data


def getBrokerAppConfig():
  with open('../config/brokerapp.json', 'r') as brokerapp:
    jsonUserData = json.load(brokerapp)
    return jsonUserData
