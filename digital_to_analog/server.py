
"""read and process data from force sensor"""

import zmq


def server_socket():
    context = zmq.Context()

    # socket to talk to client
    server_socket = context.socket(zmq.REP)
    server_socket.bind("tcp://*:5555")

    # iterate through requests of data
    while True:
        incoming = server_socket.recv_json()
        outgoing = 0.7
        server_socket.send_json(outgoing)


if __name__ == "__main__":
    server_socket()
