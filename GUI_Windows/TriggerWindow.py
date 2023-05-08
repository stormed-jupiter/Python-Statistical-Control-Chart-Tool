import customtkinter as ctk
from tkinter import messagebox


class AddNewTrigger(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("500x500")
        self.title(f"Create New Trigger")
        self.root_app = self.master.root_app
        self.trigger_selection = ctk.StringVar()
        self.trigger_name = ctk.StringVar()
        self.source_selection = ctk.StringVar()
        self.calc_size = ctk.StringVar()
        self.kwarg_val = ctk.StringVar()
        self.trigger_settings_frame = None
        self.trigger_kwargs = None

        self.columnconfigure(0, weight=1)

        self.source_and_function_frame = ctk.CTkFrame(self)
        self.source_and_function_frame.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.source_and_function_frame.columnconfigure(0, weight=1)
        self.source_and_function_frame.columnconfigure(1, weight=1)

        self.name_label = ctk.CTkLabel(self.source_and_function_frame, text='Name:')
        self.name_entry = ctk.CTkEntry(self.source_and_function_frame, textvariable=self.trigger_name)
        self.name_label.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.valid_trigger_functions = ['Std Dev Away From Mean', 'High Run', 'Consistently Increasing', 'Consistently Increasing']
        self.trigger_picker = ctk.CTkComboBox(self.source_and_function_frame, values=self.valid_trigger_functions,
                                              command=self.select_function, variable=self.trigger_selection)
        self.trigger_picker.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        self.trigger_picker_label = ctk.CTkLabel(self.source_and_function_frame, text='Select Trigger Function')
        self.trigger_picker_label.grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        self.valid_sources = []
        if self.root_app.data_state.data_source is not None:
            self.valid_sources.append('Data')
        if self.root_app.data_state.central_location_statistic is not None:
            self.valid_sources.append('CentralLocationStatistic')
        if self.root_app.data_state.spread_statistic is not None:
            self.valid_sources.append('SpreadStatistic')

        self.source_picker = ctk.CTkComboBox(self.source_and_function_frame, values=self.valid_sources,
                                             variable=self.source_selection)
        self.source_picker.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        self.source_picker_label = ctk.CTkLabel(self.source_and_function_frame, text='Select Data Source')
        self.source_picker_label.grid(row=2, column=0, padx=5, pady=5, sticky='ew')

        self.calc_size_entry = ctk.CTkEntry(self.source_and_function_frame, textvariable=self.calc_size)
        self.calc_size_label = ctk.CTkLabel(self.source_and_function_frame, text='Select duration (ms) of data for calculations')
        self.calc_size_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        self.calc_size_label.grid(row=3, column=0, padx=5, pady=5, sticky='ew')

        self.save_button = ctk.CTkButton(self, text='Save', command=self.save_trigger)
        self.save_button.grid(row=2, column=0, padx=5, pady=10, sticky='e')

    def select_function(self, value):
        selected_function = self.trigger_selection.get()

        self.trigger_settings_frame = ctk.CTkFrame(self)
        self.trigger_settings_frame.columnconfigure(0, weight=1)

        if selected_function in ('Consistently Increasing', 'Consistently Increasing'):
            return

        if selected_function == 'Std Dev Away From Mean':
            self.kwarg_val_entry_text = 'Enter Number of Std Dev from Mean to Trigger'
        if selected_function == 'High Run':
            self.kwarg_val_entry_text = 'Enter threshold value'

        self.kwarg_val_entry_label = ctk.CTkLabel(self.trigger_settings_frame, text=self.kwarg_val_entry_text)
        self.kwarg_val_entry = ctk.CTkEntry(self.trigger_settings_frame, placeholder_text='1', textvariable=self.kwarg_val)
        self.kwarg_val_entry_label.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        self.kwarg_val_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')

        self.trigger_settings_frame.grid(row=1, column=0, padx=5, pady=10, sticky='ew')

    def save_trigger(self):
        error_messages = []
        name = self.trigger_name.get()
        source = self.source_selection.get()
        trigger_func = self.trigger_selection.get()
        calc_size = self.calc_size.get()
        trigger_kwargs = None

        if not name or name is None:
            error_messages.append('Name must be provided')

        if trigger_func and trigger_func is not None:
            if trigger_func in ('High Run', 'Std Dev Away From Mean'):
                trigger_kwarg_val = self.kwarg_val.get()
                if not trigger_kwarg_val or trigger_kwarg_val is None:
                    error_messages.append('trigger function must be configured')
                else:
                    if trigger_func == 'High Run':
                        trigger_kwargs = {'threshold': float(trigger_kwarg_val)}
                    else:
                        trigger_kwargs = {'std_dev_factor': float(trigger_kwarg_val)}
        else:
            error_messages.append('Trigger function must be selected')

        if not source or source is None:
            error_messages.append('Data source must be selected')

        if not calc_size or calc_size is None:
            error_messages.append('Calculation size must be provided')

        if error_messages:
            messagebox.showinfo(title="Warning", message=', '.join(error_messages))
        else:
            match source:
                case 'Data':
                    source_buffer = self.root_app.data_state.data_source
                case 'CentralLocationStatistic':
                    source_buffer = self.root_app.data_state.central_location_statistic
                case 'SpreadStatistic':
                    source_buffer = self.root_app.data_state.spread_statistic
                case _:
                    source_buffer = self.root_app.data_state.central_location_statistic

            trigger_dict = {"source": source,
                            "name": name,
                            "source_buffer_name": source_buffer.name,
                            "trigger_function": trigger_func,
                            "window_size": int(calc_size),
                            "window_type": 'ms',
                            "active": True}

            if trigger_kwargs:
                trigger_dict = trigger_dict | {"trigger_kwargs": trigger_kwargs}

            if 'Triggers' in self.root_app.data_state.save_state_reference:
                if type(self.root_app.data_state.save_state_reference['Triggers']) == list:
                    self.root_app.data_state.save_state_reference['Triggers'].append(trigger_dict)
                else:
                    self.root_app.data_state.save_state_reference['Triggers'] = [trigger_dict]
            else:
                self.root_app.data_state.save_state_reference['Triggers'] = [trigger_dict]

            new_trigger = self.root_app.data_state.create_trigger_from_dict(trigger_dict | {"buffer": source_buffer})
            self.root_app.data_state.add_trigger_state(new_trigger)
            self.master.layout_trigger_frames()
            self.destroy()


class TriggerFrame(ctk.CTkFrame):
    def __init__(self, master, state, trigger_state):
        super().__init__(master)
        self.root_app = self.master.root_app
        self.data_state = state
        self.trigger_state = trigger_state

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=1)

        self.trigger_data_source_label = ctk.CTkLabel(self, text='Trigger Data Source',
                                                      font=ctk.CTkFont(weight='bold', size=10))
        self.trigger_data_source_label.grid(row=0, column=0, padx=5, pady=5, sticky='ew')

        self.trigger_name_label = ctk.CTkLabel(self, text='Trigger Name', font=ctk.CTkFont(weight='bold', size=10))
        self.trigger_name_label.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        self.trigger_data_source = ctk.CTkLabel(self, text=trigger_state.trigger.source)
        self.trigger_data_source.grid(row=1, column=0, padx=5, pady=0, sticky='ew')
        self.trigger_name = ctk.CTkLabel(self, text=trigger_state.name)
        self.trigger_name.grid(row=1, column=1, padx=5, pady=0, sticky='ew')
        self.delete_button = ctk.CTkButton(self, text='Delete', command=self.delete_trigger)
        self.delete_button.grid(row=1, column=2, padx=5, pady=0, sticky='e')

    def delete_trigger(self):
        delete_confirm = messagebox.askyesno(title='Confirmation',
                                             message='Are you sure you want to delete this trigger?')

        if not delete_confirm or delete_confirm is None:
            return

        self.data_state.trigger_states.remove(self.trigger_state)
        self.trigger_state = None
        self.master.layout_trigger_frames()
        self.destroy()


class TriggerListFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.root_app = self.master.root_app
        self.columnconfigure(0, weight=3)
        self.trigger_frames = []

        self.columnconfigure(0, weight=1)
        self.layout_trigger_frames()

    def layout_trigger_frames(self):
        if self.trigger_frames:
            for current_trigger_frame in self.trigger_frames:
                current_trigger_frame.destroy()

        for i, trigger_state in enumerate(self.master.root_app.data_state.trigger_states):
            trigger_frame = TriggerFrame(self, state=self.master.root_app.data_state, trigger_state=trigger_state)
            trigger_frame.grid(row=i, column=0, sticky='ew', padx=5, pady=5)
            self.trigger_frames.append(trigger_frame)


class TriggerWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x800")
        self.title("Trigger Configuration")
        self.root_app = self.master.root
        self.data_state = self.root_app.data_state
        self.add_trigger_window = None

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="Active Triggers", font=ctk.CTkFont(size=16, weight="bold"))
        self.label.grid(row=0, column=0, padx=10, pady=(5, 10), sticky='ew')

        self.add_trigger_button = ctk.CTkButton(self, text='Add New Trigger', command=self.add_new_trigger)
        self.add_trigger_button.grid(row=1, column=0, padx=10, pady=10, sticky='e')

        self.trigger_list_frame = TriggerListFrame(self)
        self.trigger_list_frame.grid(row=2, column=0, padx=10, pady=15, sticky='ew')

    def layout_trigger_frames(self):
        self.trigger_list_frame.layout_trigger_frames()

    def add_new_trigger(self):
        if self.add_trigger_window is None or not self.add_trigger_window.winfo_exists():
            self.add_trigger_window = AddNewTrigger(self)
        self.add_trigger_window.lift()
        self.add_trigger_window.attributes('-topmost', True)
        self.add_trigger_window.after_idle(self.add_trigger_window.attributes, '-topmost', False)


