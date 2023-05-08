import numpy as np
import Buffer
import functools
import ewma
import scipy


def simple_average(data: Buffer.Buffer, size, size_type):
    return np.mean(data.data)


def simple_moving_average(data: Buffer.Buffer, size, size_type='ms'):
    if len(data) == 1:
        return np.mean(data.tail_data(1))

    if size_type == 'count':
        if len(data) < size:
            return np.mean(data.data)
        else:
            return np.mean(data.tail_data(size))
    elif size_type in ('ms', 's'):
        return np.mean(data.tail_data_by_time_duration(size))


def exponentially_weighed_moving_average(data: Buffer.Buffer, size, size_type='ms', alpha=0.01):
    if len(data) == 1:
        return data.tail_data(1)
    if size_type == 'count':
        if len(data) < size:
            return ewma.ewma_vectorized_safe(data.data, alpha=alpha)
        else:
            return ewma.ewma_vectorized_safe(data.tail_data(size), alpha=alpha)
    elif size_type in ('ms', 's'):
        return ewma.ewma_vectorized_safe(data.tail_data_by_time_duration(size), alpha=alpha)


def std_dev(data: Buffer.Buffer, size, size_type='ms'):
    if len(data) == 1:
        return np.std(data.tail_data(1))

    if size_type == 'count':
        if len(data) < size:
            return np.std(data.data)
        else:
            return np.std(data.tail_data(size))
    elif size_type in ('ms', 's'):
        return np.std(data.tail_data_by_time_duration(size))


def variance(data: Buffer.Buffer, size, size_type='ms'):
    if len(data) == 1:
        return np.var(data.tail_data(1))

    if size_type == 'count':
        if len(data) < size:
            return np.var(data.data)
        else:
            return np.var(data.tail_data(size))
    elif size_type in ('ms', 's'):
        return np.var(data.tail_data_by_time_duration(size))


def geometric_mean(data: Buffer.Buffer, size, size_type='ms'):
    if len(data) == 1:
        return scipy.stats.mstats.gmean(data.tail_data(1), nan_policy='omit')

    if size_type == 'count':
        if len(data) < size:
            return scipy.stats.mstats.gmean(data.data, nan_policy='omit')
        else:
            return scipy.stats.mstats.gmean(data.tail_data(size), nan_policy='omit')
    elif size_type in ('ms', 's'):
        return scipy.stats.mstats.gmean(data.tail_data_by_time_duration(size), nan_policy='omit')


central_location_statistic_function_map = {'simple_moving_average': simple_moving_average,
                                           'exponentially_weighed_moving_average': exponentially_weighed_moving_average}
                                           # 'simple_average': simple_average}

spread_statistic_function_map = {'std_dev': std_dev, 'variance': variance}


def get_statistic_function(function_name: str, function_kwargs: dict):
    # TODO implement safety for kwargs having keyword not supported by the relevant function. Inspect the function?
    statistic_function_map = central_location_statistic_function_map | spread_statistic_function_map
    stat_function = statistic_function_map[function_name]
    return functools.partial(stat_function, **function_kwargs) if function_kwargs else stat_function


class StatBuffer(Buffer.Buffer):
    def __init__(self, name: str, data_buffer: Buffer.DataBuffer, stat_function_name: str, capacity_type: str, data_name: str,
                 capacity: int = Buffer.DEFAULT_BUFFER_SIZE, fill_kwargs: dict = None, plot=True):
        self.data_name = data_name
        self.stat_function_name = stat_function_name
        self.fill_kwargs = fill_kwargs
        self.data_buffer = data_buffer
        if fill_kwargs is None:
            self.stat_function = get_statistic_function(stat_function_name, {'data': data_buffer})
        else:
            self.stat_function = get_statistic_function(stat_function_name, {'data': data_buffer} | fill_kwargs)

        super().__init__(name=name, capacity=capacity, capacity_type=capacity_type, fill_function=self.fill_function)

    def fill_function(self):
        return self.data_buffer.time[-1], self.stat_function()
