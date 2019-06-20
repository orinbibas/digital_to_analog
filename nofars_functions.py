from mcculw import ul
from mcculw.enums import ULRange
from mcculw.ul import ULError
import numpy as np
from os import makedirs, path
import errno
from devices_config import device_dictionary

MAX_BOARD_NUM = 100
columns = ["timestamp", "value"]


def sample_device(board_num, channel, factor):
    # Reads an A/D input channel, and returns a voltage value only if the board is on.
    ai_range = ULRange.BIP10VOLTS

    try:
        # Get a value from the device
        value = ul.v_in(board_num, channel, ai_range)

    except ULError:
        return np.nan

    newton_value = value * factor
    return newton_value


def normalize_value(value, extremums):
    minimum_value = extremums[0]
    maximum_value = extremums[1]

    if value > maximum_value:
        return 1
    if value < minimum_value:
        return 0
    return (value - minimum_value) / (maximum_value - minimum_value)


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
            f.write(f"Timestamp, Value\n")


def volt_to_newton(volts, factor):
    return volts * factor


def detect_connections(channels_factors):
    connections = []
    for board in range(MAX_BOARD_NUM):
        for couple in channels_factors:
            sample = sample_device(board, couple[0], couple[1])
            if not np.isnan(sample):
                connections.append((board, couple[0], couple[1]))
                continue
    return connections


def parse_client_init_message(init_message: str):
    channel_factors = []
    couples = init_message.split(sep=",")
    for couple in couples:
        channel_number, serial_number = couple.split("_")
        factor = device_dictionary[serial_number]
        channel_factors.append((int(channel_number), factor))
    return channel_factors


def append_df_to_log(connection, df):
    filename = f"./log/board_{connection[0]}_channel_{connection[1]}.csv"
    with open(filename, 'a') as f:
        df.to_csv(f, header=False, index=False)


def listen_for_quit_message():
    # TODO
    # this function should check if there is a message saying "quit" from the client
    # return True if such a message was accepted, otherwise False
    return False


def get_init_message_from_client():
    # gets the init message from the client in the following format:
    # "{channelNum1}_{serialNum1},{channelNum2}_{serialNum2}..."
    # returns a string
    #     TODO
    pass


def send_normalized_value(value_to_send):
    # TODO
    pass
