import json, os, io
from typing import Any, List, Tuple
import zmq
from . import Globals
from Connection import Connection, ConnectionType
from .Drive import Drive
from mltradeshared import RNN, TSDataPreprocessor, ColumnConfig, TimeMeasurement
from mltradeshared.Trade import TradeManager, Trade
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
            "o": data_point["o"],
            "h": data_point["h"],
            "l": data_point["l"],
            "c": data_point["c"],
            "v": data_point["v"],
            "t": data_point["t"]
        }
    def start(self):
        model_path = os.path.join(os.environ["workspace"], "current_model.tar")
        Drive.download_latest_model(model_path)
        
        rnn, metadata = RNN.load_model(model_path, return_metadata=True)

        tm = TradeManager(
            balance=100000.0,
            max_trade_time=TimeMeasurement("minute", 40),
            trade_cooldown=TimeMeasurement("minute", 10),
            risk_per_trade=0.02,
            max_open_risk=0.06,
            dif_percentiles=metadata["dif_percentiles"]["data"],
            fraction_to_trade=0.05,
            max_trade_history=None,
            stop_loss_ATR=1.8,
            take_profit_ATR=3
        )

        col_config = ColumnConfig.from_json(json.dumps(metadata["col_config"]))
        preprocessor = TSDataPreprocessor(col_config=col_config)


        def set_trade_id(trade: Trade):
            order = {
                "action": "TRADE",
                "options": {
                    "action": "BUY" if trade.is_buy else "SELL",
                    "type": "MARKET",
                    "amount": round(trade.lot_size, 2),
                    "stop": trade.stop_loss,
                    "take_profit": trade.take_profit
                }
            }
            self.api.send(order)
            response = self.api.recieve(no_wait=False)
            trade.ticket_id = response["ticket_id"]
            print(f"\nFILLED {trade.ticket_id}. ({'BUY' if trade.is_buy else 'SELL'})\n")

        def close_trades(trades: List[Trade]):
            order: dict = {
                "action": "TRADE",
                "options": {
                    "action": "CLOSE",
                    "ticket_id": 1,
                }
            }
            for trade in trades:
                order["options"]["ticket_id"] = trade.ticket_id
                self.api.send(order)
                response = self.api.recieve(no_wait=False)
                print(f"\nCLOSED {trade.ticket_id}. ({'BUY' if trade.is_buy else 'SELL'}) --- Balance: {tm.balance}\n")

        self.loop = True
        while self.loop:
            # Now, we wait
            result = self.subscriber.recieve(no_wait=False)
            if result is None:
                print("Recieved invalid or no data")
                continue
            print(f"Putting {result} into model")
            data_point = self.convert_data_point(result)
            seq = preprocessor.dynamic_preprocess(data_point, seq_len=rnn.x_shape[1])
            if seq is not None:
                prediction = rnn.predict(seq)
                tm.check_open_trades(data_point, close_trades)
                print(f"Prediction: {prediction}")
                if tm.should_make_trade(prediction, data_point):
                    ATR = preprocessor.get_current_ATR(10)
                    if ATR is not None:
                        tm.make_trade(prediction, data_point, set_trade_id, ATR=ATR)
            # Get prediction
            # Send recommendation back to MQL