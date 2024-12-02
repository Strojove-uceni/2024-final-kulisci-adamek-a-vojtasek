import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import subprocess
import json

# Placeholder for YOLO classification (simulated for now)
def classify_image(image_path):
    # Normally, this would call your YOLO script
    # Example: subprocess.run(['python', 'yolo_classify.py', image_path])
    print(f"Classifying image: {image_path}")
    return ["tomato", "onion", "chicken"]  # Simulated YOLO output

# Placeholder for filtering recipes (simulated for now)
def filter_recipes(labels):
    # Normally, this would call your filtering script
    # Example: subprocess.run(['python', 'filter_recipes.py', json.dumps(labels)])
    print(f"Filtering recipes using: {labels}")
    return ["Recipe 1: Tomato Chicken Curry", "Recipe 2: Onion Chicken Soup"]  # Simulated output

# Main Application Class
class RecipeFinderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Recipe Finder")
        self.geometry("600x600")

        # Initialize shared variables
        self.image_path = None
        self.detected_labels = []
        self.filtered_recipes = []

        # Create main container frame
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Define steps (frames)
        self.frames = {}
        for F in (UploadFrame, PreviewFrame, LabelsFrame, ResultsFrame):
            frame = F(parent=self.container, app=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the first step
        self.show_frame(UploadFrame)

    def show_frame(self, frame_class):
        """Show a frame for the given class."""
        frame = self.frames[frame_class]
        frame.tkraise()


# Step 1: Upload Image Frame
class UploadFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Upload an Image", font=("Arial", 18)).pack(pady=20)

        upload_button = tk.Button(self, text="Upload Image", command=self.upload_image, width=20)
        upload_button.pack(pady=10)

    def upload_image(self):
        """Handle image upload and proceed to the preview step."""
        file_path = filedialog.askopenfilename(title="Select an Image File",
                                               filetypes=[("Image Files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.app.image_path = file_path
            self.app.show_frame(PreviewFrame)


# Step 2: Preview Image Frame
class PreviewFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.image_label = None

        self.header = tk.Label(self, text="Preview Uploaded Image", font=("Arial", 18))
        self.header.pack(pady=20)

        self.image_display = tk.Label(self)
        self.image_display.pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        reupload_button = tk.Button(button_frame, text="Reupload Image", command=self.reupload_image, width=15)
        reupload_button.grid(row=0, column=0, padx=10)

        confirm_button = tk.Button(button_frame, text="Confirm", command=self.confirm_image, width=15)
        confirm_button.grid(row=0, column=1, padx=10)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.display_image()

    def display_image(self):
        """Display the uploaded image."""
        if self.app.image_path:
            img = Image.open(self.app.image_path)
            img.thumbnail((400, 300))
            photo = ImageTk.PhotoImage(img)
            self.image_display.config(image=photo)
            self.image_display.image = photo

    def reupload_image(self):
        """Go back to the upload step."""
        self.app.show_frame(UploadFrame)

    def confirm_image(self):
        """Proceed to label detection step."""
        self.app.detected_labels = classify_image(self.app.image_path)
        self.app.show_frame(LabelsFrame)


class LabelsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Title Label
        tk.Label(self, text="Detected Ingredients", font=("Arial", 18)).pack(pady=20)

        # Listbox to display detected ingredients
        self.label_listbox = tk.Listbox(self, selectmode=tk.BROWSE, width=40, height=10)
        self.label_listbox.pack(side=tk.LEFT, fill="y", padx=5, pady=5)

        # Scrollbar for the listbox
        label_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.label_listbox.yview)
        label_scrollbar.pack(side=tk.LEFT, fill="y")
        self.label_listbox.config(yscrollcommand=label_scrollbar.set)

        # Frame for buttons and entry
        button_entry_frame = tk.Frame(self)
        button_entry_frame.pack(side=tk.LEFT, padx=20, pady=10)

        # Entry field for adding new ingredients
        tk.Label(button_entry_frame, text="Ingredient:").pack(pady=(0, 5))  # Label for the entry field
        self.label_entry = tk.Entry(button_entry_frame, width=30)
        self.label_entry.pack(pady=(0, 10))  # Spacing between the entry field and buttons

        # Add buttons
        add_button = tk.Button(button_entry_frame, text="Add", command=self.add_label, width=12)
        add_button.pack(pady=5)  # Add button

        remove_button = tk.Button(button_entry_frame, text="Remove", command=self.remove_label, width=12)
        remove_button.pack(pady=5)  # Remove button

        # Filter recipes button below the buttons
        filter_button = tk.Button(button_entry_frame, text="Filter Recipes", command=self.filter_recipes, width=15)
        filter_button.pack(pady=(20, 0))  # Add more spacing above the Filter Recipes button

        # Bind double-click to start editing
        self.label_listbox.bind("<Double-1>", self.start_edit)

    def add_label(self):
        """Add a new label to the listbox."""
        new_label = self.label_entry.get().strip().lower()
        if new_label:
            self.label_listbox.insert(tk.END, new_label)
            self.label_entry.delete(0, tk.END)

    def remove_label(self):
        """Remove the selected label(s) from the listbox."""
        selected_indices = self.label_listbox.curselection()
        for index in reversed(selected_indices):
            self.label_listbox.delete(index)

    def filter_recipes(self):
        """Filter recipes based on the labels."""
        labels = [self.label_listbox.get(idx) for idx in range(self.label_listbox.size())]
        self.app.filtered_recipes = filter_recipes(labels)  # Your filtering logic
        self.app.show_frame(ResultsFrame)

    def start_edit(self, event):
        """Start editing a label on double-click."""
        # Get the selected index
        selected_index = self.label_listbox.curselection()
        if not selected_index:
            return  # Do nothing if no item is selected
        self.selected_index = selected_index[0]

        # Get the current value
        current_value = self.label_listbox.get(self.selected_index)

        # Create an Entry widget to edit the value
        self.edit_entry = tk.Entry(self, width=40)
        self.edit_entry.insert(0, current_value)
        self.edit_entry.bind("<Return>", self.save_edit)  # Save on pressing Enter
        self.edit_entry.bind("<FocusOut>", self.save_edit)  # Save on losing focus

        # Place the Entry widget on top of the listbox item
        self.edit_entry.place(x=self.label_listbox.winfo_x(),
                              y=self.label_listbox.winfo_y() + (self.selected_index * 20))  # Approximate vertical offset

        self.edit_entry.focus()  # Focus on the Entry widget

    def save_edit(self, event):
        """Save the edited label."""
        # Get the new value from the Entry widget
        new_value = self.edit_entry.get().strip().lower()

        # Update the Listbox item
        if new_value:
            self.label_listbox.delete(self.selected_index)
            self.label_listbox.insert(self.selected_index, new_value)

        # Destroy the Entry widget
        self.edit_entry.destroy()



'''# Step 3: Edit Labels Frame
    class LabelsFrame(tk.Frame):
        def __init__(self, parent, app):
            super().__init__(parent)
            self.app = app

        tk.Label(self, text="Detected Ingredients", font=("Arial", 18)).pack(pady=20)

        # Listbox to display detected ingredients
        self.label_listbox = tk.Listbox(self, selectmode=tk.BROWSE, width=40, height=10)
        self.label_listbox.pack(side=tk.LEFT, fill="y", padx=5, pady=5)

        # Scrollbar for the listbox
        label_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.label_listbox.yview)
        label_scrollbar.pack(side=tk.LEFT, fill="y")
        self.label_listbox.config(yscrollcommand=label_scrollbar.set)

        # Frame for buttons and entry
        button_entry_frame = tk.Frame(self)
        button_entry_frame.pack(side=tk.LEFT, padx=20, pady=10)

        # Entry field for adding/editing labels
        tk.Label(button_entry_frame, text="Adjust ingredients:").pack(pady=(0, 5))  # Label for the entry field
        self.label_entry = tk.Entry(button_entry_frame, width=30)
        self.label_entry.pack(pady=(0, 10))  # Spacing between the entry field and buttons

        # Add buttons
        add_button = tk.Button(button_entry_frame, text="Add", command=self.add_label, width=12)
        add_button.pack(pady=5)  # Add button

        edit_button = tk.Button(button_entry_frame, text="Edit", command=self.edit_label, width=12)
        edit_button.pack(pady=5)  # Edit button

        remove_button = tk.Button(button_entry_frame, text="Remove", command=self.remove_label, width=12)
        remove_button.pack(pady=5)  # Remove button

        # Filter recipes button below the buttons
        filter_button = tk.Button(button_entry_frame, text="Filter Recipes", command=self.filter_recipes, width=15)
        filter_button.pack(pady=(20, 0))  # Add more spacing above the Filter Recipes button



    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.display_labels()

    def display_labels(self):
        """Display detected labels."""
        self.label_listbox.delete(0, tk.END)
        for label in self.app.detected_labels:
            self.label_listbox.insert(tk.END, label)

    def add_label(self):
        new_label = self.label_entry.get().strip().lower()
        if new_label:
            self.label_listbox.insert(tk.END, new_label)
            self.label_entry.delete(0, tk.END)

    # Edit Selected Label
    def edit_label(self):
        selected_indices = self.label_listbox.curselection()
        if len(selected_indices) != 1:
            messagebox.showwarning("Edit Label", "Please select one label to edit.")
            return

        selected_index = selected_indices[0]
        new_label = self.label_entry.get().strip().lower()
        if new_label:
            self.label_listbox.delete(selected_index)
            self.label_listbox.insert(selected_index, new_label)
            self.label_entry.delete(0, tk.END)

    def remove_label(self):
        selected_indices = self.label_listbox.curselection()
        for index in reversed(selected_indices):
            self.label_listbox.delete(index)

    def filter_recipes(self):
        labels = [self.label_listbox.get(idx) for idx in range(self.label_listbox.size())]
        self.app.filtered_recipes = filter_recipes(labels)
        self.app.show_frame(ResultsFrame)'''


# Step 4: Display Results Frame
class ResultsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Filtered Recipes", font=("Arial", 18)).pack(pady=20)

        self.results_listbox = tk.Listbox(self, width=60, height=15)
        self.results_listbox.pack(pady=10)

        back_button = tk.Button(self, text="Back to Labels", command=self.back_to_labels, width=20)
        back_button.pack(pady=10)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.display_results()

    def display_results(self):
        """Display filtered recipes."""
        self.results_listbox.delete(0, tk.END)
        for recipe in self.app.filtered_recipes:
            self.results_listbox.insert(tk.END, recipe)

    def back_to_labels(self):
        """Go back to the label editing step."""
        self.app.show_frame(LabelsFrame)


if __name__ == "__main__":
    app = RecipeFinderApp()
    app.mainloop()