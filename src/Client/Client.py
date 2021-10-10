import zmq
from . import Globals
from Connection import Connection, ConnectionType

class Client:
    def __init__(self):
        self.loop = False
        self.subscriber = Connection(ConnectionType.SUB, Globals.PUBLISHER_PORT)
        print(f"Connected to publisher on port {Globals.PUBLISHER_PORT}")

    def start(self):
        self.loop = True
        while self.loop:
            # Now, we wait
            result = self.subscriber.recieve(no_wait=False)
            if result is None:
                print("Recieved invalid or no data")
                continue
            print(f"Putting {result} into model")
            # Get prediction
            # Send recommendation back to MQL