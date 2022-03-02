import json, os, io
from typing import Any
import zmq
from . import Globals
from Connection import Connection, ConnectionType
from .Drive import Drive


class Client:
    def __init__(self):
        self.loop = False
        self.subscriber = Connection(ConnectionType.SUB, Globals.PUBLISHER_PORT)
        self.api = Connection(ConnectionType.REQ, Globals.API_PORT)


    def start(self):
        model_path = os.path.join(os.environ["workspace"], "current_model.tar")
        Drive.download_latest_model(model_path)

        # self.loop = True
        # while self.loop:
        #     # Now, we wait
        #     result = self.subscriber.recieve(no_wait=False)
        #     if result is None:
        #         print("Recieved invalid or no data")
        #         continue
        #     print(f"Putting {result} into model")
        #     print(f"Sending Trade to buy at market")
        #     buyOrder = {
        #         "action": "TRADE",
        #         "options": {
        #             "action": "BUY",
        #             "type": "MARKET",
        #             "amount": 0.01
        #         }
        #     }
        #     closeOrder = {
        #         "action": "TRADE",
        #         "options": {
        #             "action": "CLOSE",
        #             "ticket_id": 1,
        #         }
        #     }
        #     self.api.send(buyOrder)
        #     response = self.api.recieve(no_wait=False)
        #     ticket_id = response["ticket_id"]
        #     print(f"Ticket {ticket_id} created")
        #     # Get prediction
        #     # Send recommendation back to MQL