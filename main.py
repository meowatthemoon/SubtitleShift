import argparse
import re
from dataclasses import dataclass


@dataclass
class TimeStamp:
    hour : int
    minute : int
    second : int
    milisecond : int

    def add(self, hour = 0, minute = 0, second = 0, milisecond = 0):
        self.add_hour(hour)
        self.add_minute(minute)
        self.add_second(second)
        self.add_milisecond(milisecond)

    def add_hour(self, hour : int):
        self.hour += hour
        assert self.hour >= 0 and self.hour < 24, f"Error invalid resulting hour {self.hour}" 

    def add_minute(self, minute : int):
        self.minute += minute

        if self.minute >= 60:
            offset = self.minute - 60
            self.add_hour(1)
            self.minute = offset
        if self.minute < 0:
            offset = self.minute
            self.add_hour(-1)
            self.minute = 60 - offset

    def add_second(self, second : int):
        self.second += second

        if self.second >= 60:
            offset = self.second - 60
            self.add_minute(1)
            self.second = offset
        if self.second < 0:
            offset = self.second
            self.add_minute(-1)
            self.second = 60 - offset

    def add_milisecond(self, milisecond : int):
        self.milisecond += milisecond

        if self.milisecond >= 1000:
            offset = self.milisecond - 1000
            self.add_second(1)
            self.milisecond = offset
        if self.milisecond < 0:
            offset = self.milisecond
            self.add_second(-1)
            self.milisecond = 1000 - offset

    def to_string(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}:{self.second:02d},{self.milisecond:03d}"

def get_file_lines(file_path : str):
    with open(file_path, 'r') as f:
        return f.readlines()

def write_lines(file_path : str, lines : list):
    with open(file_path, 'w') as f:
        return f.writelines(lines)

def clean_up_timestamp(timestamp : str) -> TimeStamp:
    values = timestamp.split(":")
    if len(values) != 3:
        return None

    hour = int(re.sub("[^0-9]", "", values[0]))
    minute = int(re.sub("[^0-9]", "", values[1]))
    second_milisecond = values[2]
    values = second_milisecond.split(",")

    if len(values) != 2:
        return None

    second = int(re.sub("[^0-9]", "", values[0]))
    milisecond = int(re.sub("[^0-9]", "", values[1]))

    timestamp = TimeStamp(hour = hour, minute = minute, second = second, milisecond = milisecond)
    return timestamp

def parse_timestamp(timestamp : str) -> TimeStamp:
    while '\n' in timestamp:
        timestamp = timestamp.replace('\n', '')
    while ' ' in timestamp:
        timestamp = timestamp.replace(' ', '')

    timestamp = clean_up_timestamp(timestamp)
    assert timestamp is not None, f"Invalid and unrecoverable timestamp"

    return timestamp

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'Arguments')
    parser.add_argument('-H', type = int, default = 0, help = 'hour')
    parser.add_argument('-M', type = int, default = 0, help = 'minute')
    parser.add_argument('-S', type = int, default = 0, help = 'second')
    parser.add_argument('-MS', type = int, default = 0, help = 'milisecond')
    parser.add_argument('-F', type = str, help = 'file')
    args = parser.parse_args()

    assert args.H < 100 and args.M < 60 and args.S < 60 and args.MS < 1000

    source_lines = get_file_lines(args.F)
    goal_lines = []
    for line in source_lines:
        if '-->' in line:
            values = line.split(" --> ")
            start_timestamp = parse_timestamp(values[0])
            start_timestamp.add(hour = args.H, minute = args.M, second = args.S, milisecond = args.MS)

            end_timestamp = parse_timestamp(values[1])
            end_timestamp.add(hour = args.H, minute = args.M, second = args.S, milisecond = args.MS)

            line = f"{start_timestamp.to_string()} --> {end_timestamp.to_string()}\n"
        goal_lines.append(line)

    # Save
    source_file = args.F
    file_values = source_file.split(".")
    file_name = f"SHIFTED_{file_values[0]}.{file_values[1]}"
    write_lines(file_path = file_name, lines = goal_lines)


        
