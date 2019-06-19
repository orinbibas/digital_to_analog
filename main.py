import time
from datetime import datetime
from time import sleep
import numpy as np
from mcculw import ul
from mcculw.enums import ULRange
from mcculw.ul import ULError
import nofars_functions as nf
from scipy import signal


def configure():
    max_pressures = []
    connections = nf.detect_connections()
    for connection in connections:
        print(f"configuring board number {connection[0]}, channel {connection[1]}")
        board_num = connection[0]
        channel = connection[1]
        t_s = time.time()
        max_val = 0
        while True:
            value = nf.sample_device(board_num, channel)
            # print(f"value: {value}")
            max_val = value if value > max_val else max_val
            t_s2 = time.time()
            time_diff = t_s2 - t_s
            # print (time_diff)
            if time_diff > 3:
                break
        print(f"adding {max_val} to pressures")
        max_pressures.append(max_val)
        nf.write_line_to_file(connection, "w", f"Channel number {channel}\n"
                                              f"Max Pressure: {max_val} Newtons\n\n")
    return connections, max_pressures
    

def main_loop(connections, maximums):
    while True:
        # take first timestamp
        ts_1 = time.time()

        for connection in connections:
            # get the board and channel numbers
            board_number = connection[0]
            channel = connection[1]

            # sample value from device
            current_value = nf.sample_device(board_number, channel)

            if np.isnan(current_value):
                continue

            # write a line to the log file
            nf.write_line_to_file(connection, "a",
                                  f"{datetime.fromtimestamp(time.time())}, "
                                  f"{current_value}\n")

            # normalize the voltage value
            noramlized_value = nf.normalize_value(current_value, maximums[board_number])
            print (f'{noramlized_value} at {datetime.fromtimestamp(time.time())}')

            # take last timestamp
            ts_2 = time.time()

            # send to next
            nf.send_normalized_value(noramlized_value)

            
            # compute 0.01 - the timestamp differences
            sleep_time = 0.01 - (ts_2 - ts_1)
            
            # sleep for 0.01 second
            if sleep_time > 0:
                sleep(sleep_time)
            else:
                print (f'sleep was negative at {datetime.fromtimestamp(time.time())}')


if __name__ == "__main__":
    connections, maximum_pressures = configure()

    main_loop(connections, maximum_pressures)
