from mcculw import ul
from mcculw.enums import ULRange
from mcculw.ul import ULError
import numpy as np
from os import makedirs, path
import errno

MAX_BOARD_NUM = 100
CHANNELS = [1, 2, 3]
# change this to handle more channels


def send_normalized_value(value_to_send):
    # TODO
    pass

def sample_device(board_num, channel):
    # Reads an A/D input channel, and returns a voltage value only if the board is on.
    ai_range = ULRange.BIP10VOLTS

    try:
        # Get a value from the device
        value = ul.v_in(board_num, channel, ai_range)

    except ULError:
        return np.nan

    newton_value = volt_to_newton(value, channel)
    return newton_value

def normalize_value(value, maximum_value):
    if value > maximum_value:
        value = maximum_value
    if value < 0:
        value = 0
    return value / maximum_value


def write_line_to_file(connection: tuple, open_mode: str, line: str):
    filename = f"./log/board_{connection[0]}_channel_{connection[1]}.csv"
    if not path.exists(path.dirname(filename)):
        try:
            makedirs(path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    with open(filename, open_mode) as f:
        f.write(line)
        if open_mode == "w":
            f.write(f"Timestamp, Pressure\n")


def volt_to_newton(volts, channel):
    if channel == 1:
        # 2.285 mv/N
        return volts * 437.63677
    if channel == 2:
        # 2.271 mv/N
        return volts * 440.33465
    if channel == 3:
        # 2.319 mv/N
        return volts * 431.22035

    print("no valid (1-3) channel detected!")
    return volts * 440.3346


def detect_connections():
    connections = []
    for board in range(MAX_BOARD_NUM):
        for channel in CHANNELS:
            sample = sample_device(board, channel)
            if not np.isnan(sample):
                connections.append((board, channel))
                continue
    return connections

