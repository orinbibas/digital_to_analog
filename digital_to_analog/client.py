
"""game interface"""

import zmq


def initialize_client_socket():
    context = zmq.Context()

    # socket to talk to server
    client_socket = context.socket(zmq.REQ)
    client_socket.connect("tcp://localhost:5555")
    return client_socket


def game_client(client_socket):
    client_socket.send_json("start game")

    # iterating loop for sampling - add game
    print("playing")
    for i in range(4):
        outgoing = "gimme"
        client_socket.send_json(outgoing)
        incoming = client_socket.recv_json()

        # do stuff with incoming data
        print(outgoing, incoming)


def configure_client(client_socket):
    print("configuring")
    client_socket.send_json("configure")

    for i in range(2):
        outgoing = "gimme"
        client_socket.send_json(outgoing, flags=0)
        incoming = client_socket.recv_json()

        # do stuff with incoming data
        print(outgoing, incoming)


if __name__ == "__main__":
    socket = initialize_client_socket()
    configure_client(socket)
    game_client(socket)
