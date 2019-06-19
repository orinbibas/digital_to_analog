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
    for i in range(8):
        num_board = nf.sample_device(i)
        if np.isnan(num_board):
            max_pressures.append(None)
            # nf.save_board_norm_to_file(i, np.nan)
            continue
        print(f"configuring board number {i}")
        t_s = time.time()
        max_val = num_board
        while True:
            value = nf.sample_device(i)
            # print(f"value: {value}")
            max_val = value if value > max_val else max_val
            t_s2 = time.time()
            time_diff = t_s2 - t_s
            # print (time_diff)
            if time_diff > 3:
                break
        print(f"adding {max_val} to pressures")
        max_pressures.append(max_val)
        nf.save_board_norm_to_file(i, max_val / 5)
    return max_pressures
    

def main_loop(maximums):
    while True:
        # take first timestamp
        ts_1 = time.time()

        for board_number in range(8):    
            # sample value from device
            current_value = nf.sample_device(board_number)

            if np.isnan(current_value):
                continue

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
    maximum_pressures = configure()

    main_loop(maximum_pressures)
