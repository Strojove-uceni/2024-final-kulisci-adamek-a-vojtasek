import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import subprocess

from project import paths
from project.chatGPT_API.chatptapi import chat_gpt_api
from project.classification_pipeline.classifier import IngredientClassifier
from project.classification_pipeline.clip_model_pipeline.clip_model import ClipModel
from project.recipe_dataset.filtering import recipe_filtering


# Placeholder for filtering recipes (simulated for now)
def filter_recipes1(labels):
    # Normally, this would call your filtering script
    # Example: subprocess.run(['python', 'filter_recipes.py', json.dumps(labels)])
    print(f"Filtering recipes using: {labels}")
    recipe = recipe_filtering(labels)  # Simulated output
    return labels, recipe  # Simulated output


# Placeholder for filtering recipes (simulated for now)
def filter_recipes3(labels):
    # Normally, this would call your filtering script
    # Example: subprocess.run(['python', 'filter_recipes.py', json.dumps(labels)])
    print(f"Filtering recipes using: {labels}")
    recipe = chat_gpt_api(labels)  # Simulated output
    return labels, recipe  # Simulated output

class RecipeFinderApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Application Configuration
        self.title("Recipe Finder")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        # Initialize shared variables
        self.image_path = None
        self.processed_image_path = None
        self.labels = []
        self.filtered_recipes = []

        # Container for frames
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # Define frames
        self.frames = {}
        for F in (UploadFrame, ComparisonFrame, ResultsFrame1, ResultsFrame3):
            frame = F(parent=self.container, app=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the first frame
        self.show_frame(UploadFrame)

    def show_frame(self, frame_class):
        """Display a specific frame."""
        frame = self.frames[frame_class]
        frame.tkraise()

    def call_yolo_and_cliper(self, images_folder):
        """Call YOLO and CLIP scripts to process the image and extract labels."""
        try:
            # Simulate YOLO script call (replace with actual call)
            classifier = IngredientClassifier()
            images, ingreds = classifier.inference(images_folder)
            if images:
                for name, image in images.items():
                    image_path = f"{paths.config["annotated_images"]}/{os.path.basename(name)}"
                    image.save(image_path)
            self.processed_image_path = list(ingreds.keys())[0] # Replace with actual processed image path
            print("Processed image path:", self.processed_image_path)
            self.labels = list(ingreds.values())[0]
        except Exception as e:
            print("Error:", e)
            messagebox.showerror("Error", "Failed to process the image.")
            self.processed_image_path = None
            self.labels = None
        return image_path

class UploadFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Set the frame to fill the available space
        self.pack(fill="both", expand=True)

        # Upload Button
        tk.Label(self, text="Upload an Image", font=("Arial", 20)).pack(pady=20)
        tk.Button(self, text="Upload Image", font=("Arial", 14), command=self.upload_image).pack(pady=20, expand=True)

    def upload_image(self):
        """Handle image upload and call YOLO/CLIPER."""
        file_path = filedialog.askopenfilename(
            title="Select an Image File", filetypes=[("Image Files", "*.jpg *.png *.jpeg")]
        )
        if file_path:
            self.app.image_path = file_path
            print(f"Uploaded image path: {file_path}")

            self.app.call_yolo_and_cliper(paths.config["images"])
            self.app.show_frame(ComparisonFrame)


class ComparisonFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Comparison of Images", font=("Arial", 20)).pack(padx=(0,250), pady=10)

        # Image Display
        self.image_frame = tk.Frame(self)
        self.image_frame.pack(expand=True, fill="both")

        self.original_label = tk.Label(self.image_frame, text="Original Image", font=("Arial", 16))
        self.original_label.grid(row=0, column=0, padx=150, pady=10)

        self.processed_label = tk.Label(self.image_frame, text="Processed Image", font=("Arial", 16))
        self.processed_label.grid(row=0, column=1, padx=400, pady=10)

        # Frame for buttons and entry
        button_frame = tk.Frame(self)
        button_frame.pack(padx=300, pady=10)

        # Filter recipes button below the buttons
        filter_button1 = tk.Button(button_frame, text="Filter Recipes - first dataset", font=("Arial", 20),
                                   command=self.filter_recipes1, width=35, height=2)
        filter_button1.pack(padx=(0, 250))  # Add more spacing above the Filter Recipes button

        filter_button3 = tk.Button(button_frame, text="Filter Recipes - GPT API", font=("Arial", 20),
                                   command=self.filter_recipes3, width=35, height=2)
        filter_button3.pack(padx=(0, 250))  # Add more spacing above the Filter Recipes button

    def tkraise(self, *args, **kwargs):
        """Raise the frame and dynamically update the images."""
        super().tkraise(*args, **kwargs)
        self.update_images()

    def update_images(self):
        """Update displayed images."""
        if not (self.app.image_path and self.app.processed_image_path):
            print("Image paths are missing.")
            return

        try:
            # Resize and display original image
            original_image = Image.open(self.app.image_path)
            print("Original image loaded with dimensions:", original_image.size)  # Debug statement
            original_resized = self.resize_image(original_image, 1000, 1000)
            self.original_image_tk = ImageTk.PhotoImage(original_resized)
            self.original_label.config(image=self.original_image_tk, text="")

            # Store the reference to avoid garbage collection
            self.original_label.image = self.original_image_tk  # Keep reference

            # Resize and display processed image
            processed_image = Image.open(self.app.processed_image_path)
            print("Processed image loaded with dimensions:", processed_image.size)  # Debug statement
            processed_resized = self.resize_image(processed_image, 1000, 1000)
            self.processed_image_tk = ImageTk.PhotoImage(processed_resized)
            self.processed_label.config(image=self.processed_image_tk, text="")

            # Store the reference to avoid garbage collection
            self.processed_label.image = self.processed_image_tk  # Keep reference

        except Exception as e:
            print("Error loading images:", e)
            self.original_label.config(text="Error loading original image")
            self.processed_label.config(text="Error loading processed image")

    def resize_image(self, image, max_width, max_height):
        """Resize the image while maintaining aspect ratio."""
        original_width, original_height = image.size
        aspect_ratio = original_width / original_height

        if max_width / aspect_ratio <= max_height:
            new_width = max_width
            new_height = int(max_width / aspect_ratio)
        else:
            new_width = int(max_height * aspect_ratio)
            new_height = max_height

        print(f"Resizing to: {new_width}x{new_height}")  # Debug statement
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


    def filter_recipes1(self):
        """Filter recipes based on the labels."""
        self.app.filtered_recipes = filter_recipes1(self.app.labels)  # Pass the detected labels
        self.app.show_frame(ResultsFrame1)

    def filter_recipes3(self):
        """Filter recipes based on the labels."""
        self.app.filtered_recipes = filter_recipes3(self.app.labels)  # Pass the detected labels
        self.app.show_frame(ResultsFrame3)
'''
class ResultsFrame1(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Filtered Recipes", font=("Arial", 18)).pack(pady=20)

        self.results_listbox = tk.Listbox(self, width=60, height=15, font=("Arial", 14))
        self.results_listbox.pack(pady=10)

        back_button = tk.Button(self, text="Back to Labels", font=("Arial", 12), command=self.back_to_labels,
                                    width=14)
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
        self.app.show_frame(ComparisonFrame)
'''

class ResultsFrame1(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # Title Label for Results Frame
        tk.Label(self, text="Filtered Recipes", font=("Arial", 18)).pack(pady=20)

        # Listbox for Ingredients
        self.ingredients_listbox = tk.Listbox(self, width=60, height=15, font=("Arial", 14))
        self.ingredients_listbox.pack(pady=10)

        # Listbox for Descriptions
        self.description_listbox = tk.Listbox(self, width=200, height=15, font=("Arial", 14))
        self.description_listbox.pack(pady=10)

        # Back Button to go back to Labels
        back_button = tk.Button(self, text="Back to Labels", font=("Arial", 12), command=self.back_to_labels, width=14)
        back_button.pack(pady=10)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.display_results()

    def display_results(self):
        """Display filtered recipes with their ingredients and description."""
        self.ingredients_listbox.delete(0, tk.END)
        self.description_listbox.delete(0, tk.END)

        # Simulate the filtered recipes from the app
        # Assuming `self.app.filtered_recipes` is a list of dictionaries with 'ingredients' and 'description'
        # Example of filtered recipe data structure:
        # { "ingredients": ["Tomato", "Onion", "Chicken"], "description": "A tasty dish with chicken." }

        ingredients, recipe = self.app.filtered_recipes
        for ingredient in ingredients:
            self.ingredients_listbox.insert(tk.END, ingredient)

            # Insert ingredients into the first Listbox

        for line in recipe:
            self.description_listbox.insert(tk.END, line)

    def back_to_labels(self):
        """Go back to the label editing step."""
        self.app.show_frame(ComparisonFrame)
    # Step 4: Display Results Frame

class ResultsFrame3(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        tk.Label(self, text="Filtered Recipes", font=("Arial", 18)).pack(pady=20)

        self.ingredients_listbox = tk.Listbox(self, width=60, height=10, font=("Arial", 20))
        self.ingredients_listbox.pack(pady=10)

        # Listbox for Descriptions
        self.description_listbox = tk.Listbox(self, width=200, height=16, font=("Arial", 20))
        self.description_listbox.pack(pady=10)


        back_button = tk.Button(self, text="Back to Labels", font=("Arial", 15), command=self.back_to_labels, width=14)
        back_button.pack(pady=10)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        self.display_results()

    def display_results(self):
        """Display filtered recipes."""
        self.ingredients_listbox.delete(0, tk.END)
        self.description_listbox.delete(0, tk.END)

        # Simulate the filtered recipes from the app
        # Assuming `self.app.filtered_recipes` is a list of dictionaries with 'ingredients' and 'description'
        # Example of filtered recipe data structure:
        # { "ingredients": ["Tomato", "Onion", "Chicken"], "description": "A tasty dish with chicken." }

        ingredients, recipe = self.app.filtered_recipes
        for ingredient in ingredients:
            self.ingredients_listbox.insert(tk.END, ingredient)

            # Insert ingredients into the first Listbox

        max_line_length = 60  # Maximum characters per line
        for line in recipe.split('\n'):
            self.description_listbox.insert(tk.END, line)

    def back_to_labels(self):
        """Go back to the label editing step."""
        self.app.show_frame(ComparisonFrame)




if __name__ == "__main__":
    app = RecipeFinderApp()
    app.mainloop()
