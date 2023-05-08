import Trigger
import numpy as np


def get_trigger_function(name: str):
    lookup = {'High Run': high_run,
              'Consistently Increasing': consistently_increasing,
              'Consistently Decreasing': consistently_decreasing,
              'Std Dev Away From Mean': std_dev_away_from_mean}

    return lookup[name]


def std_dev_away_from_mean(trigger: Trigger.Trigger, std_dev_factor=1):
    population_mean = np.mean(trigger.buffer.data)
    population_std_dev = np.std(trigger.buffer.data)
    z_score = (np.array(trigger.current_data) - population_mean) / population_std_dev
    return any(np.abs(z_score) > std_dev_factor)


def high_run(trigger: Trigger.Trigger, threshold):
    if trigger.current_data is None:
        return False
    abs_data = [abs(d) for d in trigger.current_data]
    return all([d > threshold for d in abs_data])


def consistently_increasing(trigger: Trigger.Trigger):
    if trigger.current_data is None:
        return False
    abs_data = [abs(d) for d in trigger.current_data]
    return all(i < j for i, j in zip(abs_data, abs_data[1:]))


def consistently_decreasing(trigger: Trigger.Trigger):
    if trigger.current_data is None:
        return False
    abs_data = [abs(d) for d in trigger.current_data]
    return all(i > j for i, j in zip(abs_data, abs_data[1:]))

