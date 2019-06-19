from mcculw import ul
from mcculw.enums import ULRange
from mcculw.ul import ULError
import numpy as np
from os import makedirs, path
import errno


def send_normalized_value(value_to_send):
    # TODO
    pass

def sample_device(board_num):
    # Reads an A/D input channel, and returns a voltage value only if the board is on.
    channel = 2
    ai_range = ULRange.BIP10VOLTS

    try:
        # Get a value from the device
        value = ul.v_in(board_num, channel, ai_range)

    except ULError:
        return np.nan
    return value

def normalize_value(value, maximum_value):
    if value > maximum_value:
        value = maximum_value
    if value < 0:
        value = 0
    return value / maximum_value


def save_board_norm_to_file(board_number: int, norm_value: float):
    filename = f"./Norms/board_{board_number}.txt"
    if not path.exists(path.dirname(filename)):
        try:
            makedirs(path.dirname(filename))
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise
    with open(filename, "w") as f:
        f.write(f"Max Pressure value: {norm_value} Neutons\n")


