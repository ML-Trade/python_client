# Singletons not required in python
# Just import * as <name>
import zmq
import requests

gist_url = "https://gist.githubusercontent.com/bigboiblue/cb668007714195333fd9a0c79a6946ee/raw/global_config.json"
global_config_json = requests.get(gist_url).json()

# TODO: put timeframe and symbol in here (get from MQL client)

PUBLISHER_PORT = global_config_json["PUBLISHER_PORT"]
API_PORT = global_config_json["API_PORT"]
context = zmq.Context()