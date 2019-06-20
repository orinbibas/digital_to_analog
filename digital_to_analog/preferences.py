#This file contains:
import os
#Channel names: leave 'None' if not connected.
#if connected: enter channel number minus 1 (for 1 enter 0, for 2 enter 1, for 3 enter 2)
channels= [('0', 0),
('1', 'LW43893'),
('2', 'LW43894'),
('3', 0),
('4', 0),
('5', 0),
('6', 0),
('7', 0)]
#picture names

#game maximal time in seconds
max_time = 30

#screen properties (optional right now)
dw = 600
dh = 476


#path to save file
path_to_save = os.getcwd()
