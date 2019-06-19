
"""game interface"""

import zmq


def client_socket():
    context = zmq.Context()

    # socket to talk to server
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    n = 10

    # do n requests waiting each time for response
    for request in range(n):
        outgoing = b"hello"
        socket.send(outgoing)
        incoming = socket.recv()

        print(f"request # {request}: {outgoing} {incoming}")
    socket.send(b"0")


if __name__ == "__main__":
    client_socket()
