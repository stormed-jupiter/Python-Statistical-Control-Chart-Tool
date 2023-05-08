import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pathlib
import os


class FilePathFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.root_app = self.master.root_app

        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=1)

        if self.root_app.data_state.data_source is None:
            self.file_name_entry_default_text = "Target Data File Path"
        else:
            self.file_name_entry_default_text = self.root_app.data_state.data_source.filepath
        self.title_label = ctk.CTkLabel(self, text="Data File Path (Required)", fg_color="gray30", corner_radius=6)
        self.title_label.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="ew", columnspan=2)

        self.file_name_entry = ctk.CTkEntry(self, placeholder_text=self.file_name_entry_default_text)
        self.file_name_entry.grid(row=1, column=0, sticky='ew', padx=5, pady=20)

        self.file_name_browse_button = ctk.CTkButton(self, text="Browse", command=self.file_name_browser)
        self.file_name_browse_button.grid(row=1, column=1, sticky='e', padx=5, pady=20)

    def file_name_browser(self):
        f = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select data file",
                                       filetypes=(
                                       ("Text files", "*.txt*"), ("csv files", "*.csv*"), ("all files", "*.*")))
        if not f or f is None:
            return
        self.file_name_entry.delete(0, tk.END)
        self.file_name_entry.insert(0, str(pathlib.Path(f).resolve()))


class FileStructureFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.root_app = self.master.root_app

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Target File Structure (Optional)", fg_color="gray30", corner_radius=6)
        self.title_label.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="ew", columnspan=2)

        # Delimiter section
        self.delimiter_frame = ctk.CTkFrame(self)
        self.delimiter_frame.columnconfigure(0, weight=1)
        self.delimiter_combo_box_label = ctk.CTkLabel(self.delimiter_frame, text="Delimiter:")
        self.delimiter_combo_box_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='ew')
        self.delimiter_combo_box = ctk.CTkComboBox(self.delimiter_frame,
                                                   values=["space", "comma", "tab", "pipe", "semi-colon"])
        self.delimiter_combo_box.grid(row=1, column=0, padx=10, pady=(5, 0), sticky='ew')
        self.delimiter_frame.grid(row=1, column=0, padx=5, pady=(5, 10))

        # Data Index Position
        self.index_frame = ctk.CTkFrame(self)
        self.index_frame.columnconfigure(0, weight=1)
        self.index_entry_label = ctk.CTkLabel(self.index_frame, text="Data column position (zero is the first):")
        self.index_entry_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky='ew')
        self.index_entry = ctk.CTkEntry(self.index_frame, placeholder_text="0")
        self.index_entry.grid(row=1, column=0, padx=5, pady=(5, 0), sticky='ew')
        self.index_frame.grid(row=1, column=1, padx=5, pady=(5, 10))


class DataCapacityFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.root_app = self.master.root_app

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self, text="Duration of data to keep (Optional, Defaults to 60 seconds)",
                                        fg_color="gray30", corner_radius=6)
        self.title_label.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="ew", columnspan=2)

        self.capacity_label = ctk.CTkLabel(self, text="Capacity (in milliseconds):")
        self.capacity_label.grid(row=1, column=0, padx=5, pady=(5, 10))

        self.capacity_entry = ctk.CTkEntry(self, placeholder_text="60000")
        self.capacity_entry.grid(row=1, column=1, padx=5, pady=(5, 10))


class DataManagementWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("600x600")
        self.title("Data Source Management")
        self.root_app = self.master.root

        self.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="Setup the data file to be continuously read by the application",
                                  font=ctk.CTkFont(size=16, weight="bold"))
        self.label.grid(row=0, column=0, padx=10, pady=(5, 20), sticky='ew')

        # File path selection
        self.file_path_frame = FilePathFrame(self)
        self.file_path_frame.grid(row=1, column=0, padx=10, pady=20, sticky='ew')

        # Data file structure
        self.data_file_structure_frame = FileStructureFrame(self)
        self.data_file_structure_frame.grid(row=2, column=0, padx=10, pady=20, sticky='ew')

        # Data capacity
        self.data_capacity_frame = DataCapacityFrame(self)
        self.data_capacity_frame.grid(row=3, column=0, padx=10, pady=20, sticky='ew')

        # Update buttons
        self.save_button = ctk.CTkButton(self, text="Save", command=self._save_button)
        self.save_button.grid(row=4, column=0, padx=10, pady=20)

    def _save_button(self):
        new_config = {'name': 'File Reader',
                      'capacity_type': 'ms'}
        info_messages = []
        error_messages = []

        new_file_path = self.file_path_frame.file_name_entry.get()
        if new_file_path is not None and pathlib.Path(new_file_path).exists():
            new_file_path = str(pathlib.Path(new_file_path).resolve())
            new_config = new_config | {'filepath': new_file_path}
        else:
            error_messages.append('Filepath not valid or not provided. A valid filepath must be provided')

        new_capacity = self.data_capacity_frame.capacity_entry.get()
        if new_capacity is not None and new_capacity and str(new_capacity).isnumeric():
            new_capacity = int(new_capacity)
            new_config = new_config | {'capacity': new_capacity}
        else:
            info_messages.append('Capacity invalid or not provided; using default value. (Capacity must be an integer)')
            new_config = new_config | {'capacity': 60000}

        new_delimiter = self.data_file_structure_frame.delimiter_combo_box.get()
        if new_delimiter and new_delimiter in ("space", "comma", "tab", "pipe", "semi-colon"):
            new_config = new_config | {'seperator': new_delimiter}
        else:
            info_messages.append('File delimiter invalid or not provided; using default value of a space.')
            new_config = new_config | {'seperator': ' '}

        new_data_position = self.data_file_structure_frame.index_entry.get()
        if new_data_position is not None and str(new_data_position).isnumeric():
            new_data_position = int(new_data_position)
            new_config = new_config | {'data_position': new_data_position}
        else:
            info_messages.append('File data position invalid or not provided; using default value of 0.')
            new_config = new_config | {'data_position': 0}

        if not error_messages:
            if not self.root_app.data_state.save_state_reference:
                self.root_app.data_state.save_state_reference = {}
            self.root_app.data_state.save_state_reference["DataSource"] = new_config
            self.root_app.data_state.populate_data_source()
            self.root_app.stop_animation()
            self.root_app.clear_all_data()
            messagebox.showinfo(title="Success", message="Data source successfully updated,"
                                                         " chart will reset to a blank paused state")
        else:
            messagebox.showwarning(title="Failure", message=''.join(error_messages))
