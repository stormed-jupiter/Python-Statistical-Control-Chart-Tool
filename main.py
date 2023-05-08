import State
from GUI_Windows import DataManagementWindow, SettingsWindows, StatisticsWindow, TriggerWindow

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib import pyplot as plt
import matplotlib.animation as animation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import customtkinter as ctk


class App(ctk.CTk):
    def __init__(self, state: State.State):
        super().__init__()
        self.data_state = state
        self.plotting_active = False
        self.animation_interval = 100
        self.plot_raw_time_values = False
        self.show_data_legend = True
        self.show_stats_legend = True
        self.data_legend_location = 'lower right'
        self.stat_legend_location = 'lower right'

        # Setup window
        self.title('Statistical Process Charts')

        # Setup Control Frame
        self.grid_columnconfigure(0, weight=0)

    def clear_data(self):
        if self.data_state.data_source and self.data_state.data_source is not None:
            self.data_state.data_source.clear_data()

    def clear_stat_data(self):
        if self.data_state.central_location_statistic and self.data_state.central_location_statistic is not None:
            self.data_state.central_location_statistic.clear_data()
        if self.data_state.spread_statistic and self.data_state.spread_statistic is not None:
            self.data_state.spread_statistic.clear_data()

    def clear_all_data(self):
        self.clear_data()
        self.clear_stat_data()

    @staticmethod
    def change_chart_ylims(axis_type: str, limits: tuple):
        match axis_type:
            case "DataSource":
                axis = ax_data
            case "CentralLocationStatistic":
                axis = ax_central_stat
            case "SpreadStatistic":
                axis = ax_spread_stat
            case _:
                axis = ax_central_stat
        axis.set_ylim(limits)

    @staticmethod
    def reset_chart_ylims(axis_type: str):
        match axis_type:
            case "DataSource":
                axis = ax_data
            case "CentralLocationStatistic":
                axis = ax_central_stat
            case "SpreadStatistic":
                axis = ax_spread_stat
            case _:
                axis = ax_central_stat
        axis.relim()
        axis.autoscale_view()

    def _plot_data_source(self):
        # Plot the data source
        if self.data_state.data_source is not None:
            self.data_state.data_source.fill_next_frame()
            ax_data.cla()
            if self.plot_raw_time_values:
                ax_data.plot(self.data_state.data_source.time, self.data_state.data_source.data,
                             label=self.data_state.data_source.name)
            else:
                # fmt is needed for plot_date b/c it defaults to a scatter plot
                ax_data.plot_date(self.data_state.data_source.timestamps, self.data_state.data_source.data,
                                  fmt='-', label=self.data_state.data_source.name)

    def _plot_central_location_statistic(self):
        # Plotting the central location statistic
        if self.data_state.central_location_statistic is not None:
            self.data_state.central_location_statistic.fill_next_frame()
            ax_central_stat.cla()
            if self.plot_raw_time_values:
                ax_central_stat.plot(self.data_state.central_location_statistic.time,
                                     self.data_state.central_location_statistic.data,
                                     label=self.data_state.central_location_statistic.name)
            else:
                ax_central_stat.plot_date(self.data_state.central_location_statistic.timestamps,
                                          self.data_state.central_location_statistic.data,
                                          fmt='-', label=self.data_state.central_location_statistic.name)
            ax_central_stat.set_ylabel(str(self.data_state.central_location_statistic.name))

    def _plot_spread_statistic(self):
        # Plotting the spread statistic
        if self.data_state.spread_statistic is not None:
            self.data_state.spread_statistic.fill_next_frame()
            ax_spread_stat.cla()
            if self.plot_raw_time_values:
                ax_spread_stat.plot(self.data_state.spread_statistic.time,
                                    self.data_state.spread_statistic.data,
                                    label=self.data_state.spread_statistic.name)
            else:
                ax_spread_stat.plot_date(self.data_state.spread_statistic.timestamps,
                                         self.data_state.spread_statistic.data,
                                         fmt='m-', label=self.data_state.spread_statistic.name)
            ax_spread_stat.set_ylabel(str(self.data_state.spread_statistic.name))

    def _plot_triggers(self):
        if self.data_state.trigger_states:
            for trigger_state in self.data_state.trigger_states:
                trigger = trigger_state.trigger

                if trigger.active:
                    if trigger.run():
                        trigger_state.plots.add_trigger_plot(trigger)

                    match trigger.source:
                        case "Data":
                            plot_axis = ax_data
                        case "CentralLocationStatistic":
                            plot_axis = ax_central_stat
                        case "SpreadStatistic":
                            plot_axis = ax_spread_stat
                        case _:
                            plot_axis = "CentralLocationStatistic"

                    if trigger_state.plots:
                        # Remove old plots
                        trigger_state.plots.remove_old_plot_data(old_time=self.data_state.data_source.time[0])
                        for trigger_plot in trigger_state.plots:
                            if self.plot_raw_time_values:
                                plot_axis.plot(trigger_plot.time, trigger_plot.data, fmt='r-',
                                               linewidth=2, label=trigger.name)
                            else:
                                plot_axis.plot_date(trigger_plot.timestamps, trigger_plot.data,
                                                    fmt='r-', linewidth=2, label=trigger.name)

    def _plot_stat_legends(self):
        if self.show_stats_legend:
            all_lines = []
            all_labels = []

            if self.data_state.central_location_statistic is not None:
                central_stat_lines, central_stat_labels = ax_central_stat.get_legend_handles_labels()
                all_lines.append(central_stat_lines)
                all_labels.append(central_stat_labels)

            if self.data_state.spread_statistic is not None:
                spread_stat_lines, spread_stat_labels = ax_spread_stat.get_legend_handles_labels()
                all_lines.append(spread_stat_lines)
                all_labels.append(spread_stat_labels)

            if all_lines and all_labels:
                lines = all_lines.pop()
                labels = all_labels.pop()
                while all_lines:
                    lines += all_lines.pop()
                while all_labels:
                    labels += all_labels.pop()

                unique = [(line, label) for i, (line, label) in enumerate(zip(lines, labels)) if label not in labels[:i]]
                ax_spread_stat.legend(*zip(*unique), loc=self.stat_legend_location)

    def _plot_data_legends(self):
        if self.show_data_legend:
            all_lines = []
            all_labels = []

            if self.data_state.data_source is not None:
                data_stat_lines, data_stat_labels = ax_data.get_legend_handles_labels()
                all_lines.append(data_stat_lines)
                all_labels.append(data_stat_labels)

            if all_lines and all_labels:
                lines = all_lines.pop()
                labels = all_labels.pop()
                while all_lines:
                    lines += all_lines.pop()
                while all_labels:
                    labels += all_labels.pop()

                unique = [(line, label) for i, (line, label) in enumerate(zip(lines, labels)) if label not in labels[:i]]
                ax_data.legend(*zip(*unique), loc=self.data_legend_location)

    def animate(self, i):
        if not self.plotting_active:
            # # Plot the origin to ensure graph is populated and sized appropriately
            ax_data.cla()
            ax_central_stat.cla()
            ax_spread_stat.cla()
            ax_data.plot([0], [0])
            ax_central_stat.plot([0], [0])
            ax_spread_stat.plot([0], [0])
        else:
            self._plot_data_source()
            self._plot_central_location_statistic()
            self._plot_spread_statistic()
            self._plot_triggers()
            self._plot_data_legends()
            self._plot_stat_legends()
        self.update()

    def stop_animation(self):
        if ani:
            ani.pause()
            self.clear_all_data()
            ax_data.cla()
            ax_central_stat.cla()
            ax_spread_stat.cla()

    def start_animation(self):
        self.plotting_active = True
        ani.resume()
        messagebox.showinfo(title="Success", message="Chart resumed")


class AppMenu(tk.Menu):
    def __init__(self, app_root: App):
        super().__init__(app_root)
        self.root = app_root
        self.root.config(menu=self)
        self.data_window = None
        self.settings_window = None
        self.statistics_window = None
        self.trigger_window = None

        # File Menu
        self.file_menu = tk.Menu(self, tearoff=False)
        self.file_menu.add_command(label='Load Save File', command=self.load_file)
        self.file_menu.add_command(label='Save', command=self.save_file)
        self.file_menu.add_command(label='Exit', command=self.root.destroy)
        self.add_cascade(label="File", menu=self.file_menu, underline=0)

        # Data and Stats Menu
        self.data_menu = tk.Menu(self, tearoff=False)
        self.data_menu.add_command(label='Data Source Setup', command=self.open_data_window)
        self.data_menu.add_command(label='Statistics Setup', command=self.open_statistics_window)
        self.add_cascade(label="Data and Statistics", menu=self.data_menu, underline=0)

        # Trigger Menu
        self.trigger_menu = tk.Menu(self, tearoff=False)
        self.trigger_menu.add_command(label='Setup Triggers', command=self.open_trigger_window)
        self.add_cascade(label="Triggers", menu=self.trigger_menu, underline=0)

        # Settings Menu
        self.settings_menu = tk.Menu(self, tearoff=False)
        self.settings_menu.add_command(label='General Chart Settings', command=self.open_settings_window)
        self.add_cascade(label="Settings", menu=self.settings_menu, underline=0)

        # Run Menu
        self.run_menu = tk.Menu(self, tearoff=False)
        self.run_menu.add_command(label='Reset and Stop Chart', command=self.root.stop_animation)
        self.run_menu.add_command(label='Start Chart', command=self.root.start_animation)
        self.add_cascade(label="Run", menu=self.run_menu, underline=0)

    def load_file(self):
        f = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select save file",
                                       filetypes=(("JSON files", "*.json*"), ("all files", "*.*")))
        if not f or f is None:
            return

        self.root.data_state.open_save_file(f)
        self.root.data_state.populate_state_from_reference()

    def save_file(self):
        f = filedialog.asksaveasfilename(filetypes=(("JSON files", "*.json*"), ("all files", "*.*")),
                                         defaultextension=".json")
        if not f or f is None:  # asksaveasfilename return `None` if dialog closed with "cancel".
            return
        self.root.data_state.save_state_to_file(f)

    def open_data_window(self):
        if self.data_window is None or not self.data_window.winfo_exists():
            self.data_window = DataManagementWindow.DataManagementWindow(self)
        self.data_window.lift()
        self.data_window.attributes('-topmost', True)
        self.data_window.after_idle(self.data_window.attributes, '-topmost', False)

    def open_settings_window(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindows.PlotSettingsWindow(self)
        self.settings_window.lift()
        self.settings_window.attributes('-topmost', True)
        self.settings_window.after_idle(self.settings_window.attributes, '-topmost', False)

    def open_statistics_window(self):
        if self.root.data_state.data_source is None:
            messagebox.showinfo(title="Warning", message="Please configure a data source prior to statistics setup.")
        else:
            if self.statistics_window is None or not self.statistics_window.winfo_exists():
                self.statistics_window = StatisticsWindow.StatisticsWindow(self)
            self.statistics_window.lift()
            self.statistics_window.attributes('-topmost', True)
            self.statistics_window.after_idle(self.statistics_window.attributes, '-topmost', False)

    def open_trigger_window(self):
        if self.root.data_state.data_source is None\
                or (self.root.data_state.central_location_statistic is None
                    and self.root.data_state.spread_statistic is None):
            messagebox.showinfo(title="Warning", message="Please configure a data source and a statistic prior to trigger setup.")
        else:
            if self.trigger_window is None or not self.trigger_window.winfo_exists():
                self.trigger_window = TriggerWindow.TriggerWindow(self)
            self.trigger_window.lift()
            self.trigger_window.attributes('-topmost', True)
            self.trigger_window.after_idle(self.trigger_window.attributes, '-topmost', False)


ctk.set_appearance_mode("dark")
app_state = State.State()
app = App(app_state)
app_menu = AppMenu(app)

app.grid_rowconfigure(1, weight=1)
fig = plt.figure(figsize=(18, 9))
plot_canvas = FigureCanvasTkAgg(fig, app)
plot_canvas.get_tk_widget().grid(column=1, row=1)
app.option_add('*tearOff', False)
ax_data = plt.subplot(121)
ax_central_stat = plt.subplot(122)
ax_spread_stat = ax_central_stat.twinx()
ani = animation.FuncAnimation(fig, app.animate, interval=app.animation_interval, blit=False)
ani.pause()

app.mainloop()
