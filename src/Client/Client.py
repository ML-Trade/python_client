import zmq
from . import Globals
from Connection import Connection, ConnectionType

class Client:
    def __init__(self):
        self.loop = False
        # self.connection = Connection(ConnectionType.SUB, Globals.PUBLISHER_PORT)
        print(f"Connected to publisher on port {Globals.PUBLISHER_PORT}")

    def start(self):
        self.loop = True
        sub = Globals.context.socket(zmq.SUB)
        sub.connect("tcp://0.0.0.0:25000")
        sub.subscribe("")
        print("CONNECTION BITHC")
        while self.loop:
            ret = sub.recv_string()
            print(ret)
            # Now, we wait
            # result = self.connection.recieve(no_wait=False)
            # if result is None:
            #     continue
            # print(f"Putting {result} into model")
            # Get prediction
            # Send recommendation back to MQL