import time
from datetime import datetime
from time import sleep
import numpy as np
import digital_to_analog as nf
import pandas as pd
import zmq


def configure(socket):
    # get the "channel_serialNum" message from the client
    init_message = socket.recv_json()
    socket.send_json("gotit")
    # # for testing
    # init_message = "2_LW36910,3_LW36908"
    connections = nf.parse_client_init_message(init_message)

    connections = nf.detect_connections(connections)

    # finding max pressure
    # print("Please press.")
    t_s = time.time()
    while True:
        for connection in connections:
            # print(f"configuring board number {connection[0]}, channel {connection[1]}")
            value = connection.sample_device(board_num=connection.board_number)
            # print(f"value: {value}")
            connection.max_pressure = value if value > connection.max_pressure else connection.max_pressure
        t_s2 = time.time()
        time_diff = t_s2 - t_s
        # print (time_diff)
        if time_diff > 3:
            break

    # finding min pressure
    # print("Please do not press.")
    t_s = time.time()
    while True:
        for connection in connections:
            # print(f"configuring board number {connection[0]}, channel {connection[1]}")
            value = connection.sample_device(board_num=connection.board_number)
            # print(f"value: {value}")
            connection.min_pressure = value if value < connection.min_pressure else connection.min_pressure
        t_s2 = time.time()
        time_diff = t_s2 - t_s
        # print (time_diff)
        if time_diff > 3:
            break

    for connection in connections:
        connection.max_pressure *= 0.2
        connection.write_line_to_file("w", f"Channel number {connection.channel_number}\n"
                                               f"Max Pressure: {connection.max_pressure} Newtons\n\n")
    return connections


def main_loop(connections, socket):
    for connection in connections:
        connection.df = pd.DataFrame(columns=nf.columns)

    while True:
        # take first timestamp
        ts_1 = time.time()

        for connection in connections:
            # sample value from device
            current_value = connection.sample_device(board_num=connection.board_number)

            if np.isnan(current_value):
                continue

            # normalize the voltage value
            noramlized_value = nf.normalize_value(current_value,
                                                  [connection.max_pressure, connection.min_pressure])
            # print (f'{noramlized_value} at {datetime.fromtimestamp(time.time())}')

            connection.df = connection.df.append(
                {"timestamp": datetime.fromtimestamp(ts_1),
                 "value": current_value}, ignore_index=True)

            # take last timestamp
            ts_2 = time.time()

            # compute 0.01 - the timestamp differences
            sleep_time = 0.01 - (ts_2 - ts_1)

            # sleep for 0.01 second
            if sleep_time > 0:
                sleep(sleep_time)
            # else:
            #     print (f'sleep was negative at {datetime.fromtimestamp(time.time())}')

            # send to next
            try:
                incoming = socket.recv_json(flags=zmq.NOBLOCK)
                if incoming == 2:
                    df_list = [connection.df for connection in connections]
                    socket.send_json("gottit")
                    return df_list
                print(noramlized_value)
                socket.send_json(noramlized_value)

            except zmq.error.ZMQError:
                continue


def wrap_up(connections, df_list):
    for index, connection in enumerate(connections):
        nf.append_df_to_log(connection, df_list[index])
        df_list[index] = pd.DataFrame(columns=nf.columns)
    return


def server_socket():
    context = zmq.Context()

    # socket to talk to client
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")

    # iterate through requests of data
    while True:
        incoming = socket.recv_json()
        socket.send_json("gotit")
        if incoming == 0:
            connections = configure(socket)
            continue
        elif incoming == 1:
            df_list = main_loop(connections, socket)
            wrap_up(connections, df_list)
            exit(0)
            break


if __name__ == "__main__":
    server_socket()
