import os
from tkinter import TclError, filedialog
from PIL import Image
import customtkinter
from src.Frames.scrollable_frame import ScrollableFrame


# This is a patch to override a library function, so I can have a transparent background on hover
# I know this is jank, but I'm tired of annoying error messages that mean nothing to me
def patched_on_enter(self, *args):
    try:
        if self._image_label is not None:
            self._image_label.configure(bg=self._apply_appearance_mode(""))
    except TclError:
        pass


customtkinter.windows.widgets.ctk_button.CTkButton._on_enter = patched_on_enter


# Databases frame class
class Databases(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Create a scrollable frame below the buttons
        self.scrollable_frame = ScrollableFrame(self, command=self.database_info_button)
        self.scrollable_frame.pack(side="top", fill="both", expand=True, padx=20, pady=(10, 10))  # Adjust bottom padding for the static section

        # Create a static section at the bottom
        self.static_section = customtkinter.CTkFrame(self)
        self.static_section.pack(side="bottom", fill="x", padx=20, pady=(0, 10))

        # Add buttons to the static section
        self.add_button = customtkinter.CTkButton(self.static_section, text="Add", command=self.add_button_clicked)
        self.remove_button = customtkinter.CTkButton(self.static_section, text="Remove", command=self.remove_button_clicked)

        self.add_button.pack(side="left", padx=(20, 10), pady=10)
        self.remove_button.pack(side="left", padx=(10, 20), pady=10)

        # sample add items, fix the current_dir shenanigans
        current_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        current_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        for i in range(5):  # add items with images
            self.scrollable_frame.add_item(f"Databases {i}", image=customtkinter.CTkImage(
                Image.open(os.path.join(current_dir, "icons", "database_light.png"))), button_image=customtkinter.CTkImage(
                Image.open(os.path.join(current_dir, "icons", "info_light.png"))))

    def database_info_button(self, item):
        print(f"example info database: {item}")

    def add_button_clicked(self):
        AddWindow(self, corner_radius=0, fg_color="transparent")

    def remove_button_clicked(self):
        print("remove button clicked")
        # if self.scrollable_frame.selected_item:
        #     self.scrollable_frame.remove_item(self.scrollable_frame.selected_item)
        #     self.scrollable_frame.selected_item = None
        #     self.scrollable_frame.selected_row = None
        # else:
        #     print("No item selected to remove")


class AddWindow(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.new_window = customtkinter.CTkToplevel()  # Create a new top-level window
        self.new_window.title("Add Database")
        self.new_window.geometry("600x300")

        # Configure the grid for the new window to take up the entire window
        self.new_window.grid_rowconfigure(0, weight=1)
        self.new_window.grid_columnconfigure(0, weight=1)

        # Create the frame that takes up the entire window
        frame = customtkinter.CTkFrame(self.new_window, corner_radius=5)
        frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        frame.grid_rowconfigure(5, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        # Dropdown for choosing local/remote
        option_menu = customtkinter.CTkOptionMenu(frame, values=["Local", "Remote"], command=self.option_menu_callback)
        option_menu.set("Local")
        option_menu.grid(row=0, column=1, sticky="n", padx=5, pady=(10, 5))

        # Choosing path
        path_label = customtkinter.CTkLabel(frame, text="No path selected")
        path_label.grid(row=1, column=1, sticky="n", padx=5, pady=(5, 0))

        select_path_button = customtkinter.CTkButton(frame, text="Select Path", command=lambda: self.select_path(path_label))
        select_path_button.grid(row=2, column=1, sticky="n", padx=5, pady=5)

        # Submit button
        submit_button = customtkinter.CTkButton(frame, text="Add Database", command=lambda: self.submit_data(option_menu.get(),
                                                                                                             path_label.text))
        submit_button.grid(row=5, column=1, sticky="s", padx=5, pady=(5, 10))

    def select_path(self, path_label):
        path = filedialog.askdirectory()
        if path:
            path_label.configure(text=path)

    def submit_data(self, db_type, path):
        print(f"Database Type: {db_type}")
        print(f"Path: {path}")

    def option_menu_callback(self, choice):
        print("optionmenu dropdown clicked:", choice)
