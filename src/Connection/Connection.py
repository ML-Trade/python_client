from typing import Dict, List, Union
import zmq
from enum import Enum
from Client.Globals import context
import json

class ConnectionType(Enum):
    PAIR = 0
    PUB = 1
    SUB = 2
    REQ = 3
    REP = 4
    DEALER = 5
    ROUTER = 6
    PULL = 7
    PUSH = 8
    XPUB = 9
    XSUB = 10
    STREAM = 11

# Typing for a deserialised JSON value
JSONValue = Union[str, bool, int, float]
JSONDict = Dict[str, JSONValue]

class Connection:
    def __init__(self, connectionType: ConnectionType, port: int) -> None:
        self.socket = context.socket(connectionType.value)
        self.socket.connect(f"tcp://localhost:{port}")
        self.socket.subscribe('')
        self.port = port
     
    
    def recieve(self, no_wait = True) -> Union[JSONDict, None]:
        """Receives message from zmq socket, deserialises the JSON, `returns` JSON in dict"""
        message = None
        if no_wait:
            message = self.socket.recv_string(flags=zmq.NOBLOCK)
        else:
            message = self.socket.recv_string()
        return json.loads(message)


    def recieveAll(self) -> List[JSONDict]:
        """Gets messages using NO_BLOCK flag until no more can be received.
        `returns` an array of dicts (each dict is deserialised JSON)"""
        jsonDicts = []
        shouldContinue = True
        while shouldContinue:
            message = self.recieve(no_wait=True)
            if message is not None:
                jsonDicts.append(message)
            else:
                shouldContinue = False
        return jsonDicts
