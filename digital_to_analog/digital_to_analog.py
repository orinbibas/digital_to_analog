from mcculw import ul
from mcculw.enums import ULRange
from mcculw.ul import ULError
import numpy as np
from os import makedirs, path
import errno
from devices_config import device_dictionary

MAX_BOARD_NUM = 100
columns = ["timestamp", "value"]


class Connection:
    def __init__(self, board_number=None, channel_number=None,
                 max_pressure=0, min_pressure=0, factor=None):
        self.board_number = board_number
        self.channel_number = channel_number
        self.max_pressure = max_pressure
        self.min_pressure = min_pressure
        self.volt_to_newton_factor = factor
        self.df = None


    def sample_device(self, board_num):

        # Reads an A/D input channel, and returns a voltage value only if the board is on.
        ai_range = ULRange.BIP10VOLTS

        try:
            # Get a value from the device
            value = ul.v_in(board_num, self.channel_number, ai_range)

        except ULError:
            return np.nan

        newton_value = value * self.volt_to_newton_factor
        return newton_value


    def write_line_to_file(self, open_mode: str, line: str):
        filename = f"./log/board_{self.board_number}_channel_{self.channel_number}.csv"
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


def normalize_value(value, extremums):
    minimum_value = extremums[0]
    maximum_value = extremums[1]

    if value > maximum_value:
        return 1
    if value < minimum_value:
        return 0
    return (value - minimum_value) / (maximum_value - minimum_value)


def volt_to_newton(volts, factor):
    return volts * factor


def detect_connections(connections):
    for board in range(MAX_BOARD_NUM):
        for connection in connections:
            sample = connection.sample_device(board_num=board)
            if not np.isnan(sample):
                connection.board_number = board
                continue
    return connections


def parse_client_init_message(init_message: str):
    connections = []
    couples = init_message.split(sep=",")
    for couple in couples:
        channel_number, serial_number = couple.split("_")
        factor = device_dictionary[serial_number]
        connections.append(Connection(channel_number=int(channel_number), factor=factor))
    return connections


def append_df_to_log(connection, df):
    filename = f"./log/board_{connection[0]}_channel_{connection[1]}.csv"
    with open(filename, 'a') as f:
        df.to_csv(f, header=False, index=False)

#This file contains:
import os
#Channel names: leave 'None' if not connected.
#if connected: enter channel number minus 1 (for 1 enter 0, for 2 enter 1, for 3 enter 2)
channel1= None
channel2= None
channel3= None

#picture names

#game maximal time in seconds
max_time = 30

#screen properties (optional right now)
dw = 600
dh = 476


#path to save file
path_to_save = os.getcwd()
