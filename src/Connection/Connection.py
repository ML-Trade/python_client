from typing import Dict, List, Union
import zmq
from enum import Enum

from zmq.sugar.context import T
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
        """ # TODO: NOTE If this is run in WSL, you must connect to the IP shown from:
        grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'
        See https://superuser.com/questions/1535269/how-to-connect-wsl-to-a-windows-localhost """
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
        try:
            return json.loads(message)
        except json.JSONDecodeError:
            # This is not JSON
            return None

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
