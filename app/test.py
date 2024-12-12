import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess
import os
from tkinter import ttk  # Import ttk for Treeview


class RecipeFinderApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # App configuration
        self.title("Recipe Finder")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.exit_fullscreen())
        self.configure(bg="white")

        # Set background image
        image_path1 = "D:\\Programovani\\SU2\\GitRepos\\2024-final-kulisci-adamek-a-vojtasek\\app\\proxy-image.jpg"
        self.bg_image = Image.open(image_path1)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = tk.Label(self, image=self.bg_photo)
        self.bg_label.place(relwidth=1, relheight=1)  # Cover the full window
        self.bg_label.lower()

        # Initialize shared variables
        self.image_path = None
        self.processed_image_path = None
        self.ingredients = []

        # Create a container for all frames
        self.container = tk.Frame(self, bg="white")
        self.container.pack(fill="both", expand=True)

        # Define frames
        self.frames = {}
        for F in (UploadFrame, ComparisonFrame, LabelsFrame):
            frame = F(parent=self.container, app=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the first frame (UploadFrame)
        self.show_frame(UploadFrame)

    def show_frame(self, frame_class):
        """Show the given frame class."""
        frame = self.frames[frame_class]
        frame.tkraise()

    def exit_fullscreen(self):
        """Exit fullscreen mode."""
        self.attributes("-fullscreen", False)

    def call_yolo(self, image_path):
        """Call the YOLO script to process the image."""
        # Assuming the YOLO script takes the image path and outputs the processed image
        result = subprocess.run(['python', 'yolo_script.py', image_path], capture_output=True, text=True)
        if result.returncode == 0:
            self.processed_image_path = "processed_image.jpg"  # Path to processed image
        else:
            print("YOLO Error:", result.stderr)

    def call_cliper(self, image_path):
        """Call the CLIPER script to get labels from the processed image."""
        result = subprocess.run(['python', 'clipper_script.py', image_path], capture_output=True, text=True)
        if result.returncode == 0:
            # Extract labels from CLIPER output
            labels = result.stdout.splitlines()
            self.ingredients = labels
        else:
            print("CLIPER Error:", result.stderr)

    def save_ingredients(self):
        """Save ingredients and quantities to a text file."""
        with open("ingredients.txt", "w") as f:
            for ingredient in self.ingredients:
                f.write(f"{ingredient[0]} - {ingredient[1]}\n")


class UploadFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="white")
        self.upload_button = tk.Button(self, text="Upload Image", font=("Arial", 14), command=self.upload_image)
        self.upload_button.pack(pady=20)

        self.reupload_button = tk.Button(self, text="Reupload Image", font=("Arial", 14), command=self.reupload_image)
        self.reupload_button.pack(pady=20)

    def upload_image(self):
        """Handle the image upload."""
        file_path = filedialog.askopenfilename(title="Select an Image File",
                                               filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.app.image_path = file_path
            self.app.call_yolo(file_path)  # Call YOLO after uploading
            self.app.show_frame(ComparisonFrame)

    def reupload_image(self):
        """Reupload the image if needed."""
        self.upload_image()


class ComparisonFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="white")
        # Display the original and processed images side by side
        self.original_image = Image.open(self.app.image_path)
        self.processed_image = Image.open(self.app.processed_image_path)

        self.original_image = self.original_image.resize((400, 400))  # Resize to fit in window
        self.processed_image = self.processed_image.resize((400, 400))

        self.original_image_tk = ImageTk.PhotoImage(self.original_image)
        self.processed_image_tk = ImageTk.PhotoImage(self.processed_image)

        # Original image on the left
        self.original_label = tk.Label(self, image=self.original_image_tk)
        self.original_label.pack(side=tk.LEFT, padx=10)

        # Processed image on the right
        self.processed_label = tk.Label(self, image=self.processed_image_tk)
        self.processed_label.pack(side=tk.RIGHT, padx=10)

        # Call CLIPER to extract ingredient labels after displaying images
        self.app.call_cliper(self.app.processed_image_path)
        self.app.show_frame(LabelsFrame)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        confirm_button = tk.Button(button_frame, text="Confirm",font=("Arial", 12) , command=self.confirm_image, width=13, height=1)
        confirm_button.grid(row=0, column=1, padx=10)


class LabelsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="transparent")

        # Title Label
        tk.Label(self, text="Detected Ingredients", font=("Arial", 18)).pack(pady=20)

        # Treeview for Ingredients and Quantities
        self.tree = ttk.Treeview(self, columns=("Quantity", "Ingredient"), show="headings", height=15)
        self.tree.heading("Quantity", text= "Quantity")
        self.tree.heading("Ingredient", text="Ingredient")
        self.tree.column( "Quantity", width=200, anchor="center")
        self.tree.column("Ingredient", width=100, anchor="center")
        self.tree.pack(pady=20)

        # Add/Remove/Edit buttons
        buttons_frame = tk.Frame(self, bg="lightblue")
        buttons_frame.pack(pady=10)

        add_button = tk.Button(buttons_frame, text="Add", font=("Arial", 14), command=self.add_label)
        add_button.pack(side="left", padx=10)

        edit_button = tk.Button(buttons_frame, text="Edit", font=("Arial", 14), command=self.edit_label)
        edit_button.pack(side="left", padx=10)

        remove_button = tk.Button(buttons_frame, text="Remove", font=("Arial", 14), command=self.remove_label)
        remove_button.pack(side="left", padx=10)

        # Export button
        export_button = tk.Button(self, text="Export to File", font=("Arial", 14), command=self.export_to_file)
        export_button.pack(pady=20)

        self.app = app

    def add_label(self):
        """Add a new ingredient and its quantity."""
        ingredient = filedialog.askstring("Add Ingredient", "Enter ingredient name:")
        if ingredient:
            quantity = filedialog.askstring("Add Quantity", "Enter quantity (e.g., '200g', '1 cup'):")
            if quantity:
                self.tree.insert("", tk.END, values=(ingredient, quantity))

    def edit_label(self):
        """Edit the selected ingredient or its quantity."""
        selected_item = self.tree.selection()
        if selected_item:
            ingredient, quantity = self.tree.item(selected_item, "values")
            new_ingredient = filedialog.askstring("Edit Ingredient", "Edit ingredient name:", initialvalue=ingredient)
            new_quantity = filedialog.askstring("Edit Quantity", "Edit quantity:", initialvalue=quantity)
            if new_ingredient and new_quantity:
                self.tree.item(selected_item, values=(new_ingredient, new_quantity))

    def remove_label(self):
        """Remove the selected ingredient."""
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)

    def export_to_file(self):
        """Export ingredients and quantities to a .txt file."""
        with open("ingredients.txt", "w") as f:
            for row in self.tree.get_children():
                ingredient, quantity = self.tree.item(row, "values")
                f.write(f"{ingredient}: {quantity}\n")
        messagebox.showinfo("Success", "Ingredients exported successfully!")



if __name__ == "__main__":
    app = RecipeFinderApp()
    app.mainloop()


'''
        # Listbox to display detected ingredients
        self.ingredients_listbox = tk.Listbox(self, selectmode=tk.BROWSE, width=40, height=10, font=("Arial", 14))
        self.ingredients_listbox.pack(side=tk.LEFT, fill="y", padx=5, pady=5)

        # Scrollbar for the listbox
        label_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.ingredients_listbox.yview)
        label_scrollbar.pack(side=tk.LEFT, fill="y")
        self.ingredients_listbox.config(yscrollcommand=label_scrollbar.set)

        # Frame for buttons and entry
        button_entry_frame = tk.Frame(self)
        button_entry_frame.pack(side=tk.LEFT, padx=20, pady=10)

        # Save button
        self.save_button = tk.Button(self, text="Save Ingredients", font=("Arial", 14), command=self.save_ingredients)
        self.save_button.pack(pady=20)

        # Bind double-click to start editing
        self.ingredients_listbox.bind("<Double-1>", self.start_edit)

        # Entry field for adding new ingredients
        tk.Label(button_entry_frame, text="Ingredient:", font=("Arial", 20)).pack(pady=(0, 5))  # Label for the entry field
        self.label_entry = tk.Entry(button_entry_frame, width=30)
        self.label_entry.pack(pady=(0, 10))  # Spacing between the entry field and buttons

        # Export button
        export_button = tk.Button(self, text="Export to File", font=("Arial", 14), command=self.export_to_file)
        export_button.pack(pady=20)

        self.app = app

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.display_labels()

    def display_labels(self):
        """Display detected labels."""
        self.ingredients_listbox.delete(0, tk.END)
        for label in self.app.detected_labels:
            self.ingredients_listbox.insert(tk.END, label)

    def add_label(self):
        """Add a new label to the listbox."""
        new_label = self.label_entry.get().strip().lower()
        if new_label:
            self.ingredients_listbox.insert(tk.END, new_label)
            self.label_entry.delete(0, tk.END)

    def remove_label(self):
        """Remove the selected label(s) from the listbox."""
        selected_indices = self.ingredients_listbox.curselection()
        for index in reversed(selected_indices):
            self.ingredients_listbox.delete(index)

    def start_edit(self, event):
        """Start editing a label on double-click."""
        # Get the selected index
        selected_index = self.ingredients_listbox.curselection()
        if not selected_index:
            return  # Do nothing if no item is selected
        self.selected_index = selected_index[0]

        # Get the current value
        current_value = self.ingredients_listbox.get(self.selected_index)

        # Create an Entry widget to edit the value
        self.edit_entry = tk.Entry(self, width=40)
        self.edit_entry.insert(0, current_value)
        self.edit_entry.bind("<Return>", self.save_edit)  # Save on pressing Enter
        self.edit_entry.bind("<FocusOut>", self.save_edit)  # Save on losing focus

        # Place the Entry widget on top of the listbox item
        self.edit_entry.place(x=self.ingredients_listbox.winfo_x(),
                              y=self.ingredients_listbox.winfo_y() + (self.selected_index * 20))  # Approximate vertical offset

        self.edit_entry.focus()  # Focus on the Entry widget

    def save_edit(self, event):
        """Save the edited label."""
        # Get the new value from the Entry widget
        new_value = self.edit_entry.get().strip().lower()

        # Update the Listbox item
        if new_value:
            self.ingredients_listbox.delete(self.selected_index)
            self.ingredients_listbox.insert(self.selected_index, new_value)

        # Destroy the Entry widget
        self.edit_entry.destroy()


    def export_to_file(self):
        """Export labels to a .txt file."""
        with open("ingredients.txt", "w") as f:
            for item in self.ingredients_listbox.get(0, tk.END):
                f.write(item + "\n")
        messagebox.showinfo("Success", "Ingredients exported successfully!")
'''

