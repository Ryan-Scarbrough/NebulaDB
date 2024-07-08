import customtkinter


class ScrollableFrame(customtkinter.CTkScrollableFrame):
    def __init__(self, master, command=None, **kwargs):
        super().__init__(master, **kwargs)
        self.command = command
        self.label_list = []
        self.button_list = []
        self.selected_item = None  # Variable to track the selected item
        self.selected_row = None  # Variable to track the selected row

    def add_item(self, item, image=None, button_text="", button_image=None):
        row_index = len(self.label_list)

        # Defining the button to have an empty string as over color so it stays transparent. This isnt allowed
        # and throws an error, but does not have an effect on functionality.
        button = customtkinter.CTkButton(self, text=button_text, width=10, height=10, image=button_image, fg_color="transparent", hover_color="")
        label = customtkinter.CTkLabel(self, text=item, image=image, compound="left", padx=5, anchor="w")

        if self.command is not None:
            button.configure(command=lambda: self.command(item))

        button.grid(row=row_index, column=0, pady=(0, 10), padx=5)
        label.grid(row=row_index, column=1, pady=(0, 10), sticky="w")

        # Bind click event to the label and button to select the row
        label.bind("<Button-1>", lambda e, index=row_index: self.select_item(index))
        button.bind("<Button-1>", lambda e, index=row_index: self.select_item(index))

        self.label_list.append(label)
        self.button_list.append(button)

    def select_item(self, index):
        if self.selected_row is not None:
            # Reset the color of the previously selected row
            self.label_list[self.selected_row].configure(fg_color="transparent")

        # Highlight the selected row
        self.label_list[index].configure(fg_color="gray30")

        self.selected_item = self.label_list[index].cget("text")
        self.selected_row = index

    def remove_item(self, item):
        for label, button in zip(self.label_list, self.button_list):
            if item == label.cget("text"):
                label.destroy()
                button.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                return
