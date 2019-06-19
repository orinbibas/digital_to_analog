import time
from datetime import datetime
from time import sleep
import numpy as np
import nofars_functions as nf
import pandas as pd


def configure():
    # # get the "channel_serialNum" message from the client
    # init_message = nf.get_init_message_from_client()

    # for testing
    init_message = "2_LW36910"

    channels_factors = nf.parse_client_init_message(init_message)

    min_max_pressures = []
    connections = nf.detect_connections(channels_factors)
    for connection in connections:
        print(f"configuring board number {connection[0]}, channel {connection[1]}")
        board_num = connection[0]
        channel = connection[1]
        factor = connection[2]

        # finding max pressure
        print("Please press.")
        t_s = time.time()
        max_val = 0
        while True:
            value = nf.sample_device(board_num, channel, factor)
            # print(f"value: {value}")
            max_val = value if value > max_val else max_val
            t_s2 = time.time()
            time_diff = t_s2 - t_s
            # print (time_diff)
            if time_diff > 3:
                break

        # finding min pressure
        print("Please do not press.")
        t_s = time.time()
        min_val = 0
        while True:
            value = nf.sample_device(board_num, channel, factor)
            # print(f"value: {value}")
            min_val = value if value < min_val else min_val
            t_s2 = time.time()
            time_diff = t_s2 - t_s
            # print (time_diff)
            if time_diff > 3:
                break

        if max_val == 0:
            min_max_pressures.append((0, 0.000001))
            continue
        # print(f"adding max: {max_val}, min: {min_val} to pressures")
        max_val = max_val * 0.2
        min_max_pressures.append((min_val, max_val))
        nf.write_line_to_file(connection, "w", f"Channel number {channel}\n"
                                               f"Max Pressure: {max_val} Newtons\n\n")
    return connections, min_max_pressures


def main_loop(connections, extremums):
    df_list = [pd.DataFrame(columns=nf.columns) for i in range(len(connections))]

    while True:
        # take first timestamp
        ts_1 = time.time()

        for index, connection in enumerate(connections):
            # get the board and channel numbers
            board_number = connection[0]
            channel = connection[1]

            # sample value from device
            current_value = nf.sample_device(board_number, channel, connection[2])

            if np.isnan(current_value):
                continue

            # normalize the voltage value
            noramlized_value = nf.normalize_value(current_value, extremums[index])
            # print (f'{noramlized_value} at {datetime.fromtimestamp(time.time())}')

            df_list[index] = df_list[index].append(
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
                return df_list


def wrap_up(connections, df_list):
    for index, connection in enumerate(connections):
        nf.append_df_to_log(connection, df_list[index])
        df_list[index] = pd.DataFrame(columns=nf.columns)
    return


if __name__ == "__main__":
    connections, extremum_pressures = configure()

    df_list = main_loop(connections, extremum_pressures)

    wrap_up(connections, df_list)

    exit(0)
