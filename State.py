import json
import pathlib
import Trigger
import Buffer
import statistics
import trigger_functions


class State:
    def __init__(self):
        self.data_source: Buffer.DataBuffer | None = None
        self.central_location_statistic: statistics.StatBuffer | None = None
        self.spread_statistic: statistics.StatBuffer | None = None
        self.trigger_states: list[Trigger.TriggerState] = []
        self.save_state_reference: dict | None = None

    def clear_data_source(self):
        self.data_source = None

    def clear_central_location_statistic(self):
        self.central_location_statistic = None

    def clear_spread_statistic(self):
        self.spread_statistic = None

    def open_save_file(self, file_path: str):
        path = pathlib.Path(file_path)
        if not path.exists():
            raise ValueError('File: %s not found' % str(path.resolve()))
        with path.open() as f:
            self.save_state_reference = json.load(f)

    def save_state_to_file(self, target_file):
        with open(target_file, "w") as outfile:
            json.dump(self.save_state_reference, outfile)

    def populate_data_source(self):
        data_source_dict = self.save_state_reference['DataSource']
        kwargs = {'name': data_source_dict['name'],
                  'filepath': data_source_dict['filepath'],
                  'capacity': data_source_dict['capacity'],
                  'capacity_type': data_source_dict['capacity_type']}
        if 'kwargs' in data_source_dict:
            kwargs = kwargs | data_source_dict['kwargs']
        self.data_source = Buffer.DataBuffer(**kwargs)

    def populate_statistic(self, statistic_type: str = 'CentralLocationStatistic'):

        def _create_stat_buffer(reference_dict):
            kwargs = {'name': reference_dict['name'],
                      'capacity': reference_dict['capacity'],
                      'data_buffer': self.data_source,
                      'stat_function_name': reference_dict['stat_function_name'],
                      'plot': reference_dict['plot'],
                      'capacity_type': reference_dict['capacity_type'],
                      'data_name': reference_dict['data_name']}
            if reference_dict['stat_function_kwargs']:
                kwargs['fill_kwargs'] = reference_dict['stat_function_kwargs']

            return statistics.StatBuffer(**kwargs)

        if statistic_type == 'CentralLocationStatistic':
            self.central_location_statistic = _create_stat_buffer(self.save_state_reference['CentralLocationStatistic'])
        elif statistic_type == 'SpreadStatistic':
            self.spread_statistic = _create_stat_buffer(self.save_state_reference['SpreadStatistic'])
        else:
            raise ValueError(f'Statistic type of {statistic_type} is not recognized, please verify your save file')

    def create_trigger_from_dict(self, trigger_dict: dict):

        match trigger_dict["source"]:
            case 'Data':
                source_buffer = self.data_source
            case 'CentralLocationStatistic':
                source_buffer = self.central_location_statistic
            case 'SpreadStatistic':
                source_buffer = self.spread_statistic
            case _:
                source_buffer = self.central_location_statistic

        kwargs = {"name": trigger_dict['name'],
                  "source": trigger_dict["source"],
                  "source_buffer_name": trigger_dict["source_buffer_name"],
                  "window_size": trigger_dict["window_size"],
                  "window_type": trigger_dict["window_type"],
                  "active": trigger_dict["active"],
                  "buffer": source_buffer,
                  "trigger_function": trigger_functions.get_trigger_function(trigger_dict["trigger_function"])}
        if trigger_dict["trigger_kwargs"]:
            kwargs["trigger_kwargs"] = trigger_dict["trigger_kwargs"]
        return Trigger.Trigger(**kwargs)

    def add_trigger_state(self, trigger):
        self.trigger_states.append(Trigger.TriggerState(trigger=trigger,
                                                        name=trigger.name,
                                                        plots=Trigger.TriggerPlotDataCollection()))

    def populate_trigger_states(self):
        for trigger_reference in self.save_state_reference['Triggers']:
            trigger = self.create_trigger_from_dict(trigger_reference)
            self.add_trigger_state(trigger)

    def populate_state_from_reference(self):
        if 'DataSource' in self.save_state_reference:
            self.populate_data_source()
        if 'CentralLocationStatistic' in self.save_state_reference:
            self.populate_statistic(statistic_type='CentralLocationStatistic')
        if 'SpreadStatistic' in self.save_state_reference:
            self.populate_statistic(statistic_type='SpreadStatistic')
        if 'Triggers' in self.save_state_reference:
            self.populate_trigger_states()


if __name__ == '__main__':
    save_file = r'saves/_EXAMPLE_1.json'
    state = State()
    state.open_save_file(save_file)
    state.populate_state_from_reference()
