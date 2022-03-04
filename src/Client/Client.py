import json, os, io
from typing import Any, Tuple
import zmq
from . import Globals
from Connection import Connection, ConnectionType
from .Drive import Drive
from mltradeshared import RNN, TSDataPreprocessor, ColumnConfig
from datetime import datetime
from dateutil import parser


buyOrder = {
    "action": "TRADE",
    "options": {
        "action": "BUY",
        "type": "MARKET",
        "amount": 0.01
    }
}
sellOrder = {
    "action": "TRADE",
    "options": {
        "action": "SELL",
        "type": "MARKET",
        "amount": 0.01
    }
}
closeOrder = {
    "action": "TRADE",
    "options": {
        "action": "CLOSE",
        "ticket_id": 1,
    }
}
class Client:
    def __init__(self):
        self.loop = False
        self.subscriber = Connection(ConnectionType.SUB, Globals.PUBLISHER_PORT)
        self.api = Connection(ConnectionType.REQ, Globals.API_PORT)

    def convert_data_point(self, data_point: dict) -> dict:
        return {
            "o": data_point["open"],
            "h": data_point["high"],
            "l": data_point["low"],
            "c": data_point["close"],
            "v": data_point["volume"],
            "t": parser.parse(data_point["time"]).timestamp()
        }
    def start(self):
        model_path = os.path.join(os.environ["workspace"], "current_model.tar")
        Drive.download_latest_model(model_path)
        
        rnn, col_config = RNN.load_model(model_path, return_col_config = True)
        preprocessor = TSDataPreprocessor(col_config)
        self.loop = True
        while self.loop:
            # Now, we wait
            result = self.subscriber.recieve(no_wait=False)
            if result is None:
                print("Recieved invalid or no data")
                continue
            print(f"Putting {result} into model")
            seq = preprocessor.dynamic_preprocess(self.convert_data_point(result), seq_len=rnn.x_shape[1])
            if seq is not None:
                pred = rnn.predict(seq)
                if pred[0] > pred[1]:
                    self.api.send(buyOrder)
                    print(f"Pred is {pred} so BUYING")
                else:
                    self.api.send(sellOrder)
                    print(f"Pred is {pred} so SELLING")
                response = self.api.recieve(no_wait=False)
                ticket_id = response["ticket_id"]
                print(f"Ticket {ticket_id} created")
            # Get prediction
            # Send recommendation back to MQL