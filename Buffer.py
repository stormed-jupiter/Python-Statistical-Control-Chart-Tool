import collections
from typing import Callable, Union
import time
import os
from Config import Config
from datetime import datetime


DEFAULT_BUFFER_SIZE = Config.get('DEFAULT_BUFFER_SIZE')
TIME_FACTOR = Config.get('TIME_FACTOR')


class Buffer:
    def __init__(self, name: str, fill_function: Callable,
                 capacity: int = DEFAULT_BUFFER_SIZE, capacity_type: str = 'ms'):
        self.name = name
        self.fill_function = fill_function  # Fill function should return a tuple of timestamp, datum
        self.capacity = capacity
        self.capacity_type = capacity_type
        self.data = collections.deque()
        self.time = collections.deque()
        self.timestamps = collections.deque()

    def __len__(self):
        return len(self.data)

    def clear_data(self):
        self.data = collections.deque()
        self.time = collections.deque()
        self.timestamps = collections.deque()

    def fill_next_frame(self):
        if self.capacity_type == 'points' and len(self) == self.capacity:
            self.data.popleft()
            self.time.popleft()
            self.timestamps.popleft()

        if self.capacity_type in ('ms', 's'):
            while self.get_timespan() >= self.capacity:
                self.data.popleft()
                self.time.popleft()
                self.timestamps.popleft()

        raw_time, datum = self.fill_function()
        self.time.append(raw_time)
        self.data.append(datum)
        self._add_new_timestamp(raw_time)

    def _add_new_timestamp(self, new_time: Union[int, float]):
        if self.capacity_type == 'ms':
            self.timestamps.append(datetime.fromtimestamp(new_time / 1000.0))
        elif self.capacity_type == 's':
            self.timestamps.append(datetime.fromtimestamp(new_time / 1000000.0))

    def get_timespan(self):
        if len(self) > 1:
            return self.time[-1] - self.time[0]
        else:
            return 0

    def tail_time(self, n, step: int = 1):
        if len(self.time) < n * step:
            return list(self.time)
        return [self.time[-1 - (i * step)] for i in range(n)][::-1]

    def tail_data(self, n, step: int = 1):
        if len(self.data) < n * step:
            return list(self.data)
        return [self.data[-1 - (i * step)] for i in range(n)][::-1]

    def tail_timestamps(self, n, step: int = 1) -> list:
        if len(self.timestamps) < n * step:
            return list(self.timestamps)
        return [self.timestamps[-1 - (i * step)] for i in range(n)][::-1]

    def _number_data_points_within_duration(self, duration):
        i = -1
        time_to_find = self.time[-1] - duration
        while i > -len(self) and self.time[i] >= time_to_find:
            i = i - 1
        return abs(i)

    def tail_data_by_time_duration(self, duration):
        return self.tail_data(self._number_data_points_within_duration(duration))

    def tail_time_by_time_duration(self, duration):
        return self.tail_time(self._number_data_points_within_duration(duration))

    def tail_timestamps_by_time_duration(self, duration):
        return self.tail_timestamps(self._number_data_points_within_duration(duration))


class DataBuffer(Buffer):
    def __init__(self, filepath: str, name: str, capacity_type: str, capacity: int = DEFAULT_BUFFER_SIZE,
                 fill_kwargs: dict = None):
        self.filepath = filepath
        if fill_kwargs is None:
            fill_function = time_and_file_reader(filepath)
        else:
            fill_function = time_and_file_reader(filepath=filepath, **fill_kwargs)
        super().__init__(name=name, capacity=capacity, capacity_type=capacity_type, fill_function=fill_function)


def system_time():
    # For ms time TIME_FACTOR should be 1000000
    return time.time_ns() // TIME_FACTOR


def read_n_to_last_line(filename: str, n=1):
    """Returns the nth before last line of a file (n=1 gives last line)"""
    """Taken from Jazz Weismann stackoverflow post"""
    """https://stackoverflow.com/questions/46258499/how-to-read-the-last-line-of-a-file-in-python"""
    num_newlines = 0
    with open(filename, 'rb') as f:
        try:
            f.seek(-2, os.SEEK_END)
            while num_newlines < n:
                f.seek(-2, os.SEEK_CUR)
                if f.read(1) == b'\n':
                    num_newlines += 1
        except OSError:
            f.seek(0)
        last_line = f.readline().decode()
    return last_line


def time_and_file_reader(filepath: str, seperator: str = ' ', data_position: int = 0, timestamp_position: int = None):
    # TODO Implement taking in other formats of time from a file (e.g. formatted time strings)
    if data_position == timestamp_position:
        raise ValueError(f'Data and timestamp position of file reader for "{filepath}" are the same.')

    if timestamp_position is None:
        # No timestamp position given for file reader therefore using system time in ms
        def time_and_datum():
            return system_time(), float(read_n_to_last_line(filepath).split(seperator)[data_position].strip())
    else:
        def time_and_datum():
            split_line = read_n_to_last_line(filepath).split(seperator)
            return float(split_line[timestamp_position]), float(split_line[data_position])

    return time_and_datum
