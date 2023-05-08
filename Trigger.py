import collections
from typing import Callable, Union
import Buffer
import statistics
import functools
from typing import Union
import bisect
import pathlib
import csv
from datetime import datetime
from Config import Config
from dataclasses import dataclass


TRIGGER_OUTPUT_INDIVIDUAL_FILE_DIR = Config.get('TRIGGER_OUTPUT_INDIVIDUAL_FILE_DIR')
TRIGGER_OUTPUT_DIR = Config.get('TRIGGER_OUTPUT_DIR')
TRIGGER_OUTPUT_COMBINED_FILE_NAME = Config.get('TRIGGER_OUTPUT_COMBINED_FILE_NAME')


class Trigger:
    def __init__(self, name: str, buffer: Union[Buffer.Buffer, statistics.StatBuffer], window_size: float,
                 trigger_function: Callable, source_buffer_name, output_to_file=True,
                 output_individual_file_directory=TRIGGER_OUTPUT_INDIVIDUAL_FILE_DIR,
                 output_combined_file_directory=TRIGGER_OUTPUT_DIR, output_combined_file_name=TRIGGER_OUTPUT_COMBINED_FILE_NAME,
                 trigger_kwargs=None, active=True, window_type: str = 'ms', source: str = "CentralLocationStatistic"):
        self.name = name
        self.buffer = buffer
        self.source = source
        self.source_buffer_name = source_buffer_name
        self.window_size = window_size
        self.window_type = window_type
        self.trigger_function = functools.partial(trigger_function, **trigger_kwargs) if trigger_kwargs else trigger_function
        self.active = active
        self.current_data = None
        self.current_time = None
        self.current_time_stamps = None
        self.trigger_chain_status = False
        self.trigger_chain_data = None
        self.trigger_chain_time = None
        self.trigger_chain_timestamps = None
        self.output_to_file = output_to_file
        self.output_file_individual_directory = output_individual_file_directory
        self.output_combined_file_directory = output_combined_file_directory
        self.output_combined_file_name = output_combined_file_name
        self.trigger_chain_output_file = None

    def deactivate(self):
        self.active = False

    def activate(self):
        self.active = True

    def reset_chain_status(self):
        self.trigger_chain_status = False
        self.trigger_chain_data = None
        self.trigger_chain_time = None
        self.trigger_chain_output_file = None

    def get_buffer_time_and_data(self):
        if self.window_type in ('ms', 's'):
            data = self.buffer.tail_data_by_time_duration(self.window_size)
            times = self.buffer.tail_time_by_time_duration(self.window_size)
            time_stamps = self.buffer.tail_timestamps_by_time_duration(self.window_size)
        else:
            data = self.buffer.tail_data(self.window_size)
            times = self.buffer.tail_time(self.window_size)
            time_stamps = self.buffer.tail_timestamps(self.window_size)

        return time_stamps, times, data

    def run(self):
        if not self.active:
            return False

        if self.window_type == 'ms' and self.buffer.get_timespan() < self.window_size:
            return False

        self.current_time_stamps, self.current_time, self.current_data = self.get_buffer_time_and_data()
        trigger_response = self.trigger_function(self)

        if not self.trigger_chain_status:
            # Not currently in a trigger chain
            self.trigger_chain_status = trigger_response
            if trigger_response:
                # Start trigger chain and set initial chain data and time
                self.trigger_chain_time = self.current_time
                self.trigger_chain_data = self.current_data
                self.trigger_chain_timestamps = self.current_time_stamps
                self._export_time_and_data_to_individual_file()
                self._export_time_and_data_to_combined_file()
        else:
            if trigger_response:
                # Continue the chain
                new_time_stamps, new_time, new_data = self._get_new_time_and_data()
                self._add_new_time_and_data(new_time_stamps=new_time_stamps, new_time=new_time, new_data=new_data)
                self._append_time_and_data_to_individual_file(new_time=new_time, new_data=new_data)
                self._append_time_and_data_to_combined_file(new_time=new_time, new_data=new_data)
            else:
                # Chain has ended
                self.reset_chain_status()
        return trigger_response

    def _export_time_and_data_to_individual_file(self):
        timestamp = datetime.now().strftime("%Y_%m_%d-%H%M_%S_%f")
        self.trigger_chain_output_file = pathlib.Path(self.output_file_individual_directory) / f'{timestamp}_{self.name}_trigger'
        with open(self.trigger_chain_output_file, 'w', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(zip([timestamp for i in range(len(self.trigger_chain_time))], self.trigger_chain_time, self.trigger_chain_data))

    def _append_time_and_data_to_individual_file(self, new_time, new_data):
        # Already writing to a file for the chain therefore append
        timestamp = datetime.now().strftime("%Y_%m_%d-%H%M_%S_%f")
        with open(self.trigger_chain_output_file, 'a', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(zip([timestamp], new_time, new_data))

    def _export_time_and_data_to_combined_file(self):
        timestamp = datetime.now().strftime("%Y_%m_%d-%H%M_%S_%f")
        out_file_path = pathlib.Path(self.output_combined_file_directory) / self.output_combined_file_name
        with open(out_file_path, 'w', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(zip([self.name for i in range(len(self.trigger_chain_time))],
                                 [timestamp for i in range(len(self.trigger_chain_time))],
                                 self.trigger_chain_time, self.trigger_chain_data))

    def _append_time_and_data_to_combined_file(self, new_time, new_data):
        timestamp = datetime.now().strftime("%Y_%m_%d-%H%M_%S_%f")
        out_file_path = pathlib.Path(self.output_combined_file_directory) / self.output_combined_file_name
        with open(out_file_path, 'a', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerows(zip([self.name], [timestamp], new_time, new_data))

    def _get_new_time_and_data(self):
        # Use the last saved time and find the point in the buffer where new time values start
        new_data_index = bisect.bisect_right(self.buffer.time, self.trigger_chain_time[-1])
        num_new_data_points = len(self.buffer) - new_data_index
        return self.buffer.tail_timestamps(num_new_data_points), self.buffer.tail_time(num_new_data_points), \
               self.buffer.tail_data(num_new_data_points)

    def _add_new_time_and_data(self, new_time_stamps, new_time, new_data):
        # Use the last saved time and find the point in the buffer where new time values start
        if self.trigger_chain_data is None:
            self.trigger_chain_data = []
        if self.trigger_chain_time is None:
            self.trigger_chain_time = []
        if self.trigger_chain_timestamps is None:
            self.trigger_chain_timestamps = []
        self.trigger_chain_timestamps.extend(new_time_stamps)
        self.trigger_chain_time.extend(new_time)
        self.trigger_chain_data.extend(new_data)


def combine_triggers(first_trigger: Trigger, second_trigger: Trigger, how='OR') -> Trigger:
    if first_trigger.window_size != second_trigger.window_size:
        raise ValueError('Cannot combine mismatched sized triggers')
    new_window_size = first_trigger.window_size

    if first_trigger.buffer is not second_trigger.buffer:
        raise ValueError('Buffers for the two combined triggers must match')
    new_buffer = first_trigger.buffer

    if first_trigger.window_type != second_trigger.window_type:
        raise ValueError('Time type for the two combined triggers must match')

    if how == 'OR':
        def new_function(new_trigger: Trigger):
            return first_trigger.trigger_function(new_trigger) or second_trigger.trigger_function(new_trigger)
    elif how == 'AND':
        def new_function(new_trigger: Trigger):
            return first_trigger.trigger_function(new_trigger) and second_trigger.trigger_function(new_trigger)
    elif how == 'NAND':
        def new_function(new_trigger: Trigger):
            return not (first_trigger.trigger_function(new_trigger) and second_trigger.trigger_function(new_trigger))
    elif how == 'XOR':
        def new_function(new_trigger: Trigger):
            return first_trigger.trigger_function(new_trigger) ^ second_trigger.trigger_function(new_trigger)
    else:
        raise ValueError('How must be "OR", "AND", "NAND", "XOR"')

    return Trigger(name=f'{first_trigger.name}_{how}_{second_trigger.name}',
                   buffer=new_buffer, window_size=new_window_size, trigger_function=new_function,
                   window_type=first_trigger.window_type, source_buffer_name=new_buffer.name,
                   source=first_trigger.source)


@dataclass
class TriggerPlotData:
    trigger_name: str
    data: list
    time: list
    timestamps: list
    earliest_time: Union[int, float]


class TriggerPlotDataCollection(collections.deque):
    def __init__(self):
        super().__init__()

    def remove_old_plot_data(self, old_time):
        # This method assumes that the trigger with the oldest time is in the 0 index position
        while self and self[0].earliest_time < old_time:
            self.popleft()

    def add_trigger_plot(self, activated_trigger: Trigger):
        if not activated_trigger.active:
            return None

        if len(self) > 0 and self[0].earliest_time == activated_trigger.trigger_chain_time[0]:
            # The trigger is not a new plot, but rather a continuation of a trigger chain
            self[0].data = activated_trigger.trigger_chain_data
            self[0].time = activated_trigger.trigger_chain_time
            self[0].timestamps = activated_trigger.trigger_chain_timestamps
        else:
            self.append(TriggerPlotData(trigger_name=activated_trigger.name,
                                        data=activated_trigger.trigger_chain_data,
                                        time=activated_trigger.trigger_chain_time,
                                        timestamps=activated_trigger.trigger_chain_timestamps,
                                        earliest_time=activated_trigger.trigger_chain_time[0]))


@dataclass
class TriggerState:
    plots: TriggerPlotDataCollection
    name: str
    trigger: Trigger = None
