import customtkinter as ctk


class PeriodicityFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.root_app = self.master.root_app

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Chart and Data Refresh Periodicity (milliseconds)", fg_color="gray30", corner_radius=6)
        self.title_label.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="ew", columnspan=2)

        self.periodicity_label = ctk.CTkLabel(self, text="Refresh Periodicity (ms):")
        self.periodicity_label.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        self.periodicity_entry = ctk.CTkEntry(self, placeholder_text=str(self.root_app.animation_interval))
        self.periodicity_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)

        self.save_button = ctk.CTkButton(self, text="Save", command=None)
        self.save_button.grid(row=2, column=0, padx=5, pady=5, columnspan=2)

        self.periodicity_warning_label = ctk.CTkLabel(self, text="Warning low periodicity (high frequency) can result in performance issue.")
        self.periodicity_warning_label.grid(row=3, column=0, sticky='ew', padx=5, pady=5, columnspan=2)


class DataYAxisLimitFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.root_app = self.master.root_app

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Data Chart Y Limits", fg_color="gray30", corner_radius=6)
        self.title_label.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="ew", columnspan=2)

        # Upper limits
        self.data_y_axis_upper_limit_label = ctk.CTkLabel(self, text="Y Upper Limit")
        self.data_y_axis_upper_limit_entry = ctk.CTkEntry(self, placeholder_text="")
        self.data_y_axis_upper_limit_label.grid(row=1, column=0, padx=5, pady=5)
        self.data_y_axis_upper_limit_entry.grid(row=2, column=0, padx=5, pady=5)

        # Lower limits
        self.data_y_axis_lower_limit_label = ctk.CTkLabel(self, text="Y Lower Limit")
        self.data_y_axis_lower_limit_entry = ctk.CTkEntry(self, placeholder_text="")
        self.data_y_axis_lower_limit_label.grid(row=1, column=1, padx=5, pady=5)
        self.data_y_axis_lower_limit_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        self.save_button = ctk.CTkButton(self, text="Save", command=self.save_data_ylims)
        self.save_button.grid(row=3, column=0, padx=5, pady=10)
        self.reset_button = ctk.CTkButton(self, text="Reset Axis", command=None)
        self.reset_button.grid(row=3, column=1, padx=5, pady=10)

    def save_data_ylims(self):
        ylims = (self.data_y_axis_lower_limit_entry.get(), self.data_y_axis_upper_limit_entry.get())
        self.root_app.change_chart_ylims(axis_type='DataSource', limits=ylims)


class CentralStatYAxisLimitFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.root_app = self.master.root_app

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Stat Central Location Chart Y Limits", fg_color="gray30",
                                        corner_radius=6)
        self.title_label.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="ew", columnspan=2)

        # Upper limits
        self.stat_y_axis_upper_limit_label = ctk.CTkLabel(self, text="Y Upper Limit")
        self.stat_y_axis_upper_limit_entry = ctk.CTkEntry(self, placeholder_text="")
        self.stat_y_axis_upper_limit_label.grid(row=1, column=0, padx=5, pady=5)
        self.stat_y_axis_upper_limit_entry.grid(row=2, column=0, padx=5, pady=5)

        # Lower limits
        self.stat_y_axis_lower_limit_label = ctk.CTkLabel(self, text="Y Lower Limit")
        self.stat_y_axis_lower_limit_entry = ctk.CTkEntry(self, placeholder_text="")
        self.stat_y_axis_lower_limit_label.grid(row=1, column=1, padx=5, pady=5)
        self.stat_y_axis_lower_limit_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        self.save_button = ctk.CTkButton(self, text="Save",
                                         command=self.save_central_stat_ylims())
        self.save_button.grid(row=3, column=0, padx=5, pady=10)
        self.reset_button = ctk.CTkButton(self, text="Reset Axis", command=None)
        self.reset_button.grid(row=3, column=1, padx=5, pady=10)

    def save_central_stat_ylims(self):
        ylims = (self.stat_y_axis_lower_limit_entry.get(), self.stat_y_axis_upper_limit_entry.get())
        self.root_app.change_chart_ylims(axis_type='CentralLocationStatistic', limits=ylims)


class SpreadStatYAxisLimitFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.root_app = self.master.root_app

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Stat Spread Chart Y Limits", fg_color="gray30", corner_radius=6)
        self.title_label.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="ew", columnspan=2)

        # Upper limits
        self.stat_y_axis_upper_limit_label = ctk.CTkLabel(self, text="Y Upper Limit")
        self.stat_y_axis_upper_limit_entry = ctk.CTkEntry(self, placeholder_text="")
        self.stat_y_axis_upper_limit_label.grid(row=1, column=0, padx=5, pady=5)
        self.stat_y_axis_upper_limit_entry.grid(row=2, column=0, padx=5, pady=5)

        # Lower limits
        self.stat_y_axis_lower_limit_label = ctk.CTkLabel(self, text="Y Lower Limit")
        self.stat_y_axis_lower_limit_entry = ctk.CTkEntry(self, placeholder_text="")
        self.stat_y_axis_lower_limit_label.grid(row=1, column=1, padx=5, pady=5)
        self.stat_y_axis_lower_limit_entry.grid(row=2, column=1, padx=5, pady=5)

        # Buttons
        self.save_button = ctk.CTkButton(self, text="Save",
                                         command=self.save_spread_stat_ylims())
        self.save_button.grid(row=3, column=0, padx=5, pady=10)
        self.reset_button = ctk.CTkButton(self, text="Reset Axis", command=None)
        self.reset_button.grid(row=3, column=1, padx=5, pady=10)

    def save_spread_stat_ylims(self):
        ylims = (self.stat_y_axis_lower_limit_entry.get(), self.stat_y_axis_upper_limit_entry.get())
        self.root_app.change_chart_ylims(axis_type='SpreadStatistic', limits=ylims)


class PlotSettingsWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x800")
        self.title("Plot Settings")
        self.root_app = self.master.root

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="General Chart Settings",
                                  font=ctk.CTkFont(size=16, weight="bold"))
        self.label.grid(row=0, column=0, padx=10, pady=(5, 10), sticky='ew')

        # Periodicity Settings
        self.periodicity_frame = PeriodicityFrame(self)
        self.periodicity_frame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        # Data Y Axis Limits
        self.data_y_axis_frame = DataYAxisLimitFrame(self)
        self.data_y_axis_frame.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

        # Central Stat Y Axis Limits
        self.stat_y_axis_frame = CentralStatYAxisLimitFrame(self)
        self.stat_y_axis_frame.grid(row=3, column=0, padx=10, pady=10, sticky='ew')

        # Spread Stat Y Axis Limits
        self.stat_y_axis_frame = SpreadStatYAxisLimitFrame(self)
        self.stat_y_axis_frame.grid(row=4, column=0, padx=10, pady=10, sticky='ew')
