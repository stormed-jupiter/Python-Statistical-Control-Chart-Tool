import customtkinter as ctk
from tkinter import messagebox
import statistics
import Config


class StatisticFunctionConfigWindows(ctk.CTkToplevel):
    def __init__(self, function_name: str, stat_state, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("300x300")
        self.title(f"{function_name} Configuration")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        if function_name in ('simple_moving_average', 'std_dev', 'variance'):
            self.calculation_size = ctk.StringVar()
            self.calculation_time_type = ctk.StringVar()
            self.size_entry_label = ctk.CTkLabel(self, text="Calculation Size:")
            self.size_entry = ctk.CTkEntry(self, textvariable=self.calculation_size)
            self.size_entry_label.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
            self.size_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
            self.calc_time_type_label = ctk.CTkLabel(self, text="Calculation time type:")
            self.calc_time_type_label.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
            self.calc_time_type_picker = ctk.CTkComboBox(self, values=['ms', 'points'],
                                                         variable=self.calculation_time_type)
            self.calc_time_type_picker.grid(row=2, column=1, sticky='ew', padx=5, pady=5)

            def save_config():
                size = self.calculation_size.get()
                size_type = self.calculation_time_type.get()
                if not size:
                    size = float(Config.Config.get("DEFAULT_STAT_CALC_SIZE"))
                else:
                    size = float(size)
                if not size_type:
                    size_type = 'ms'
                self.master.stat_function_kwargs = {'size': size, 'size_type': size_type}

            self.save_button = ctk.CTkButton(self, text="Save", command=save_config)
            self.save_button.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

            if stat_state is not None:
                self.calculation_size.set(str(stat_state.fill_kwargs['size']))
                self.calculation_time_type.set(str(stat_state.fill_kwargs['size_type']))
            else:
                self.calculation_size.set(str(Config.Config.get("DEFAULT_STAT_CALC_SIZE")))
                self.calculation_time_type.set('ms')

        elif function_name == 'exponentially_weighed_moving_average':
            self.calculation_size = ctk.StringVar()
            self.calculation_time_type = ctk.StringVar()
            self.alpha = ctk.StringVar()
            self.size_entry_label = ctk.CTkLabel(self, text="Calculation Size:")
            self.size_entry = ctk.CTkEntry(self, textvariable=self.calculation_size)
            self.size_entry_label.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
            self.size_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
            self.calc_time_type_label = ctk.CTkLabel(self, text="Calculation time type:")
            self.calc_time_type_label.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
            self.calc_time_type_picker = ctk.CTkComboBox(self, values=['ms', 'points'],
                                                         textvariable=self.calculation_time_type)
            self.calc_time_type_picker.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
            self.alpha_entry_label = ctk.CTkLabel(self, text="Alpha:")
            self.alpha_entry = ctk.CTkEntry(self, textvariable=self.alpha)

            def save_config():
                size = self.calculation_size.get()
                size_type = self.calculation_time_type.get()
                alpha = self.alpha.get()
                if not size:
                    size = float(Config.Config.get("DEFAULT_STAT_CALC_SIZE"))
                else:
                    size = float(size)
                if not size_type:
                    size_type = 'ms'
                if not alpha:
                    alpha = float(Config.Config.get("DEFAULT_EWMA_ALPHA"))
                else:
                    alpha = float(alpha)

                self.master.stat_function_kwargs = {'size': size, 'size_type': size_type, 'alpha': alpha}

            self.save_button = ctk.CTkButton(self, text="Save", command=save_config)
            self.save_button.grid(row=3, column=1, sticky='ew', padx=5, pady=5)

            if stat_state is not None:
                self.calculation_size.set(str(stat_state.fill_kwargs['size']))
                self.calculation_time_type.set(str(stat_state.fill_kwargs['size_type']))
                self.alpha.set(str(stat_state.fill_kwargs['alpha']))
            else:
                self.calculation_size.set(str(Config.Config.get("DEFAULT_STAT_CALC_SIZE")))
                self.calculation_time_type.set('ms')
                self.alpha.set(str(Config.Config.get("DEFAULT_EWMA_ALPHA")))


class StatisticFrame(ctk.CTkFrame):
    def __init__(self, master, type: str):
        super().__init__(master)
        self.root_app = self.master.root_app
        self.name = ctk.StringVar()
        self.calculation_size = ctk.StringVar()
        self.type = type
        self.stat_function_kwargs = None
        self.stat_function_config_menu = None

        self.valid_data_name = self.root_app.data_state.data_source.name

        if self.type == 'CentralLocationStatistic':
            self.valid_stat_functions = sorted([k for k in statistics.central_location_statistic_function_map.keys()])
        else:
            self.valid_stat_functions = sorted([k for k in statistics.spread_statistic_function_map.keys()])

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        # First row of name, save, delete
        self.name_label = ctk.CTkLabel(self, text="Name (must be unique):")
        self.name_label.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        self.name_entry = ctk.CTkEntry(self, placeholder_text='', textvariable=self.name)
        self.name_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self.save_button = ctk.CTkButton(self, text="Save", command=self.save)
        self.save_button.grid(row=0, column=2, padx=5, pady=5)
        self.delete_button = ctk.CTkButton(self, text="Delete", command=self.delete)
        self.delete_button.grid(row=0, column=3, padx=5, pady=5)

        # Second row of statistic function selection and configure
        self.stat_function_label = ctk.CTkLabel(self, text="Stat Function:")
        self.stat_function_label.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        self.stat_function_picker = ctk.CTkComboBox(self, values=self.valid_stat_functions)
        self.stat_function_picker.set(self.valid_stat_functions[0])
        self.stat_function_picker.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        self.configure_button = ctk.CTkButton(self, text="Configure Stat Function", command=self.configure_stat)
        self.configure_button.grid(row=1, column=2, sticky='ew', padx=20, pady=5, columnspan=2)

        if self.type == 'CentralLocationStatistic' and self.root_app.data_state.central_location_statistic is not None:
            self.stat_state = self.root_app.data_state.central_location_statistic
            self.name.set(self.root_app.data_state.central_location_statistic.name)
            self.stat_function_picker.set(self.root_app.data_state.central_location_statistic.stat_function_name)
        elif self.type == 'SpreadStatistic' and self.root_app.data_state.spread_statistic is not None:
            self.stat_state = self.root_app.data_state.spread_statistic
            self.name.set(self.root_app.data_state.spread_statistic.name)
            self.stat_function_picker.set(self.root_app.data_state.spread_statistic.stat_function_name)
        else:
            self.stat_state = None

    def save(self):
        new_stat_config = dict(name=self.name_entry.get(),
                               data_name=self.valid_data_name,
                               stat_function_name=self.stat_function_picker.get(),
                               capacity=self.root_app.data_state.data_source.capacity,
                               capacity_type=self.root_app.data_state.data_source.capacity_type)

        blanks = []
        for new_config_entry, new_config_value in new_stat_config.items():
            if (not new_config_value or new_config_value is None) and (new_config_entry != 'stat_function_kwargs'):
                blanks.append(new_config_entry)

        if self.stat_function_kwargs is None:
            blanks.append('Stat Function Configuration')

        if blanks:
            messagebox.showinfo(title="Warning", message="Please fill in: %s" % ', '.join(blanks))
        else:
            self.root_app.data_state.save_state_reference[self.type] = new_stat_config | {'plot': True}
            self.root_app.data_state.populate_statistic(statistic_type=self.type)
            messagebox.showinfo(title="Success", message="Statistic Created")

    def configure_stat(self):
        if self.stat_function_config_menu is None or not self.stat_function_config_menu.winfo_exists():
            self.stat_function_config_menu = StatisticFunctionConfigWindows(self.stat_function_picker.get(),
                                                                            stat_state=self.stat_state)
        self.stat_function_config_menu.lift()
        self.stat_function_config_menu.attributes('-topmost', True)
        self.stat_function_config_menu.after_idle(self.stat_function_config_menu.attributes, '-topmost', False)

    def delete(self):
        delete_confirm = messagebox.askyesno(title='Confirmation',
                                             message='Are you sure you want to delete the Central Location Statistic?')

        if not delete_confirm or delete_confirm is None:
            return

        if self.type == 'CentralLocationStatistic':
            self.root_app.data_state.clear_central_location_statistic()
        elif self.type == 'SpreadStatistic':
            self.root_app.data_state.clear_spread_statistic()


class StatisticsWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("800x400")
        self.title("Statistics Configuration")
        self.root_app = self.master.root

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="Statistics to be Calculated",
                                  font=ctk.CTkFont(size=16, weight="bold"))
        self.label.grid(row=0, column=0, padx=10, pady=(5, 10), sticky='ew')

        self.central_stat_label = ctk.CTkLabel(self, text="Central Location Statistic",
                                               font=ctk.CTkFont(size=14, weight="bold"))
        self.central_stat_label.grid(row=1, column=0, padx=10, pady=(5, 10), sticky='ew')
        self.central_statistic_frame = StatisticFrame(self, type="CentralLocationStatistic")
        self.central_statistic_frame.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

        self.spread_stat_label = ctk.CTkLabel(self, text="Spread Statistic",
                                              font=ctk.CTkFont(size=14, weight="bold"))
        self.spread_stat_label.grid(row=3, column=0, padx=10, pady=(5, 10), sticky='ew')
        self.spread_statistic_frame = StatisticFrame(self, type="SpreadStatistic")
        self.spread_statistic_frame.grid(row=4, column=0, padx=10, pady=10, sticky='ew')
