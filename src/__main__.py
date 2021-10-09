# from Client import Client
# def main():
#     client = Client()
#     client.start()

import zmq

context = zmq.Context()
def main():
    socket = context.socket(zmq.SUB)
    """ NOTE: If this is run in WSL, you must connect to the IP shown from:
    grep -m 1 nameserver /etc/resolv.conf | awk '{print $2}'
    See https://superuser.com/questions/1535269/how-to-connect-wsl-to-a-windows-localhost """
    socket.connect("tcp://localhost:25565")
    print("Connected!")
    socket.subscribe("")

    while (True):
        msg = socket.recv_string()
        print(msg)

if __name__ == "__main__":
    main()


