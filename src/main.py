import os
from PIL import Image
import customtkinter
from src.Frames import database_frame, upload_frame

# Set default color theme
customtkinter.set_default_color_theme("/Users/ryanscarbrough/Desktop/Programming Stuff/PyCharm/NebulaDB/config/theme.json")


# Event handlers for GUI interactions
def change_scaling_event(new_scaling: str):
    new_scaling_float = int(new_scaling.replace("%", "")) / 100
    customtkinter.set_widget_scaling(new_scaling_float)


def open_settings():
    print("Opening settings...")


def change_appearance_mode_event(new_appearance_mode):
    customtkinter.set_appearance_mode(new_appearance_mode)


# Main application class
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.create_navigation_frame()
        self.create_frames()
        self.setup_buttons()
        self.select_frame_by_name("home")

    def setup_window(self):
        self.title("NebulaDB")
        self.geometry("1100x580")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def create_navigation_frame(self):
        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)

        # Load and display logo image
        image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "icons")
        self.logo_image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "orion.png")), size=(75, 75))

        # Create a frame to hold the image and the text separately
        self.title_frame = customtkinter.CTkFrame(self.navigation_frame, corner_radius=0)
        self.title_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")

        # Create the logo label
        self.logo_label = customtkinter.CTkLabel(self.title_frame, image=self.logo_image, text="")
        self.logo_label.grid(row=0, column=0, padx=(0, 10))

        # Create the title label
        self.navframe_title = customtkinter.CTkLabel(self.title_frame, text="NebulaDB",
                                                     font=customtkinter.CTkFont(size=20, weight="bold"))
        self.navframe_title.grid(row=0, column=1)

    def create_frames(self):
        # Initialize frames
        self.home_frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.databases = database_frame.Databases(self, corner_radius=0, fg_color="transparent")
        self.upload = upload_frame.Upload(self, corner_radius=0, fg_color="transparent")
        self.search = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")

        # Configure grid positions for frames
        self.home_frame.grid(row=0, column=1, sticky="nsew")
        self.databases.grid(row=0, column=1, sticky="nsew")
        self.upload.grid(row=0, column=1, sticky="nsew")
        self.search.grid(row=0, column=1, sticky="nsew")

    def setup_buttons(self):
        # Navigation buttons
        self.home_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10,
                                                   text="Home", fg_color="transparent", text_color=("gray10", "gray90"),
                                                   hover_color=("gray70", "gray30"), command=self.home_button_event)
        self.home_button.grid(row=1, column=0, sticky="ew")

        self.databases_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                        border_spacing=10,
                                                        text="Databases", fg_color="transparent",
                                                        text_color=("gray10", "gray90"),
                                                        hover_color=("gray70", "gray30"),
                                                        command=self.databases_button_event)
        self.databases_button.grid(row=2, column=0, sticky="ew")

        self.upload_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                        border_spacing=10,
                                                        text="Upload", fg_color="transparent",
                                                        text_color=("gray10", "gray90"),
                                                        hover_color=("gray70", "gray30"),
                                                        command=self.upload_button_event)
        self.upload_button.grid(row=3, column=0, sticky="ew")

        self.search_button = customtkinter.CTkButton(self.navigation_frame, corner_radius=0, height=40,
                                                    border_spacing=10,
                                                    text="Search", fg_color="transparent",
                                                    text_color=("gray10", "gray90"),
                                                    hover_color=("gray70", "gray30"), command=self.search_button_event)
        self.search_button.grid(row=4, column=0, sticky="ew")

        # Settings button
        self.open_settings_button = customtkinter.CTkButton(self.navigation_frame, text="Settings",
                                                            command=open_settings)
        self.open_settings_button.grid(row=6, column=0, padx=20, pady=20, sticky="s")

    def select_frame_by_name(self, name):
        # Switch frames based on button clicks
        self.home_button.configure(fg_color=("gray75", "gray25") if name == "home" else "transparent")
        self.databases_button.configure(fg_color=("gray75", "gray25") if name == "databases" else "transparent")
        self.search_button.configure(fg_color=("gray75", "gray25") if name == "search" else "transparent")

        if name == "home":
            self.home_frame.grid(row=0, column=1, sticky="nsew")
        else:
            self.home_frame.grid_forget()
        if name == "databases":
            self.databases.grid(row=0, column=1, sticky="nsew")
        else:
            self.databases.grid_forget()
        if name == "upload":
            self.upload.grid(row=0, column=1, sticky="nsew")
        else:
            self.upload.grid_forget()
        if name == "search":
            self.search.grid(row=0, column=1, sticky="nsew")
        else:
            self.search.grid_forget()

    # Button click events
    def home_button_event(self):
        self.select_frame_by_name("home")

    def databases_button_event(self):
        self.select_frame_by_name("databases")

    def upload_button_event(self):
        self.select_frame_by_name("upload")

    def search_button_event(self):
        self.select_frame_by_name("search")


# Main entry point
if __name__ == "__main__":
    app = App()
    app.mainloop()
