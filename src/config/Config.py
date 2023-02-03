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


def get_broker_app_config():
  with open('../config/brokerapp.json', 'r') as brokerapp:
    json_user_data = json.load(brokerapp)
    return json_user_data


def get_holidays():
  with open('../config/holidays.json', 'r') as holidays:
    holidays_data = json.load(holidays)
    return holidays_data


def get_timestamps_data():
  server_config = get_server_config()
  timestamps_file_path = os.path.join(
      server_config['deployDir'], 'timestamps.json')
  if os.path.exists(timestamps_file_path) == False:
    return {}
  timestamps_file = open(timestamps_file_path, 'r')
  timestamps = json.loads(timestamps_file.read())
  return timestamps


def save_timestamps_data(timestamps={}):
  serverConfig = get_server_config()
  timestamps_file_path = os.path.join(
      serverConfig['deployDir'], 'timestamps.json')
  with open(timestamps_file_path, 'w') as timestamps_file:
    json.dump(timestamps, timestamps_file, indent=2)
  print("saved timestamps data to file " + timestamps_file_path)
