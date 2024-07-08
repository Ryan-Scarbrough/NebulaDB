import os
from tkinter import TclError
from PIL import Image
import customtkinter
from src.Frames.scrollable_frame import ScrollableFrame


# This is a patch to override a library function so I can have a transparent background on hover
# I know this is jank, but Im tired of annoying error messages that mean nothing to me
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

        # sample add items, fix the current_dir shenanigas
        current_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        current_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        for i in range(5):  # add items with images
            self.scrollable_frame.add_item(f"Database {i}", image=customtkinter.CTkImage(
                Image.open(os.path.join(current_dir, "icons", "database_light.png"))), button_image=customtkinter.CTkImage(
                Image.open(os.path.join(current_dir, "icons", "info_light.png"))))

    def database_info_button(self, item):
        print(f"example info database: {item}")

    # Function to handle data submission (can be customized)
    def submit_data(first_name, last_name, email):
        print(f"First Name: {first_name}")
        print(f"Last Name: {last_name}")
        print(f"Email: {email}")

    def add_button_clicked(self):
        new_window = customtkinter.CTkToplevel()  # Create a new top-level window
        new_window.title("Add Database")

        # Add a label to the new window
        label = customtkinter.CTkLabel(new_window, text="Enter your details:")
        label.pack(pady=10)

        # Add text fields (Entry widgets) to the new window
        entry1 = customtkinter.CTkEntry(new_window, placeholder_text="First Name")
        entry1.pack(pady=5)

        entry2 = customtkinter.CTkEntry(new_window, placeholder_text="Last Name")
        entry2.pack(pady=5)

        entry3 = customtkinter.CTkEntry(new_window, placeholder_text="Email")
        entry3.pack(pady=5)

        # Add a submit button
        submit_button = customtkinter.CTkButton(new_window, text="Add Database",
                                                command=lambda: self.submit_data(entry1.get(), entry2.get(), entry3.get()))
        submit_button.pack(pady=10)

    def remove_button_clicked(self):
        print("remove button clicked")
        # if self.scrollable_frame.selected_item:
        #     self.scrollable_frame.remove_item(self.scrollable_frame.selected_item)
        #     self.scrollable_frame.selected_item = None
        #     self.scrollable_frame.selected_row = None
        # else:
        #     print("No item selected to remove")
