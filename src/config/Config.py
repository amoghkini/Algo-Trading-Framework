import json
import os

def get_server_config():
    with open('../config/server.json', 'r') as server:
        jsonServerData = json.load(server)
        return jsonServerData


def get_system_config():
    with open('../config/system.json', 'r') as system:
        json_system_data = json.load(system)
        return json_system_data

def getBrokerAppConfig():
    with open('../config/brokerapp.json', 'r') as brokerapp:
        jsonUserData = json.load(brokerapp)
        return jsonUserData


def get_holidays():
    with open('../config/holidays.json', 'r') as holidays:
        holidaysData = json.load(holidays)
        return holidaysData

def getTimestampsData():
    serverConfig = get_server_config()
    timestampsFilePath = os.path.join(serverConfig['deployDir'], 'timestamps.json')
    if os.path.exists(timestampsFilePath) == False:
        return {}
    timestampsFile = open(timestampsFilePath, 'r')
    timestamps = json.loads(timestampsFile.read())
    return timestamps

def saveTimestampsData(timestamps = {}):
    serverConfig = get_server_config()
    timestampsFilePath = os.path.join(serverConfig['deployDir'], 'timestamps.json')
    with open(timestampsFilePath, 'w') as timestampsFile:
        json.dump(timestamps, timestampsFile, indent=2)
    print("saved timestamps data to file " + timestampsFilePath)
