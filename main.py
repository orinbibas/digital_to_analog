import time
from datetime import datetime
from time import sleep
import numpy as np
import nofars_functions as nf
import pandas as pd


def configure():
    # get the "channel_serialNum" message from the client
    init_message = nf.get_init_message_from_client()

    # # for testing
    # init_message = "2_LW36910,3_LW36908"

    connections = nf.parse_client_init_message(init_message)

    min_max_pressures = []
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


def main_loop(connections):
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

            # send to next
            nf.send_normalized_value(noramlized_value)

            # compute 0.01 - the timestamp differences
            sleep_time = 0.01 - (ts_2 - ts_1)

            # sleep for 0.01 second
            if sleep_time > 0:
                sleep(sleep_time)
            # else:
            #     print (f'sleep was negative at {datetime.fromtimestamp(time.time())}')

            if nf.listen_for_quit_message():
                df_list = [connection.df for connection in connections]
                return df_list


def wrap_up(connections, df_list):
    for index, connection in enumerate(connections):
        nf.append_df_to_log(connection, df_list[index])
        df_list[index] = pd.DataFrame(columns=nf.columns)
    return


if __name__ == "__main__":
    connections = configure()

    df_list = main_loop(connections)

    wrap_up(connections, df_list)

    exit(0)
