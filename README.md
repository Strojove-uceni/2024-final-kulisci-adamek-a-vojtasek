# Remi: Ingredient Classification and Recipe Recommendation System

## 📘 Abstract
**Remi** is an AI-powered system that classifies ingredients in an image and recommends recipes you can make with them. We leverage a combination of modern computer vision techniques like **YOLOv11** for ingredient detection and **CLIP-based classification** for more specific ingredient identification. The detected ingredients are matched against a **recipe database** to suggest dishes that can be prepared with the available ingredients or alternatively fed into the **ChatGPT API**.

The system is designed to provide fast, accurate, and practical suggestions for users looking for inspiration in the kitchen.

---

## 🚀 Features
- **Ingredient Detection**: Uses **YOLOv11m** to detect general ingredient objects from images.  
- **Ingredient Classification**: Crops detected objects and classifies them using **CLIP** embeddings and a custom label list.  
- **Recipe Suggestion**: Matches the identified ingredients against a recipe database to suggest dishes that require the available ingredients.  
- **ChatGPT Integration**: Optionally use the **ChatGPT API** to generate creative recipe suggestions.  
- **Scalability**: Supports adding more datasets, labels, and custom recipes. Also is can be separated in to two parts: the detector and the clasifier and can be tuned independantly on each other.   

---

## 📷 System Architecture / Workflow
```
             User Input (Image) 
                    ↓
          YOLOv11 Detection (Objects)
                    ↓
        Cropping & CLIP Ingredient Classification
                    ↓
          Recipe Matching (via database or ChatGPT)
                    ↓
      Recipe Suggestions 
```

---

## 📚 Methodology

### 🧑‍🔬 **1. Data Collection**
We sourced datasets for ingredients from various online sources, specifically from **Roboflow**, and combined them into a **unified COCO-like format**. This allowed us to train YOLOv11 on a larger and more diverse set of ingredient images. Additionally, since public datasets for packaged ingredients (like milk bottles, spice containers) are limited, we augmented the dataset with images containing objects like toothpaste and packaged products. 

This step was crucial since it allowed us to avoid the costly process of creating a custom-labeled dataset while ensuring the system could recognize and distinguish ingredient packaging from raw ingredients.

### ⚙️ **2. Object Detection with YOLOv11m**
We trained a **YOLOv11m** model to detect general ingredient objects in images. The model detects bounding boxes for objects like "onion", "carrot", or "tomato".

**Training details**:
- **Datasets**: Combined datasets from multiple online sources and Roboflow.  
- **Epochs**: **200** epochs with **16 batch size**.  
- **Augmentations**: Flips, color shifts, random noise, and other augmentations included in the datasets.  

### 🖼️ **3. Ingredient Classification using CLIP**
After YOLOv11 detects objects, each detected object is **cropped** and passed into a **CLIP-based classification system**.

**Why CLIP?** CLIP is a multimodal model that can classify images based on text embeddings. We created a list of custom **ingredient labels** like "tomato", "sweet potato", "beer", and so on. Each image crop is classified into one of these categories using CLIP's image-to-text similarity scores.

### 🍲 **4. Recipe Matching**
Once the ingredients are identified, they are matched against a **recipe database (CSV file)**. We filter recipes by checking if the detected ingredients are sufficient to create the recipe. If some ingredients are missing, the system informs the user which ingredients are required. 

Optionally, we can send the list of detected ingredients to **ChatGPT** to generate creative and unique recipe suggestions.

---
##  134 Classes list:
'coffee', 'egg', 'yogurt', 'strawberry', 'bell pepper', 'blueberry', 'ham', 'naan', 'buttermilk', 'chilli', 'tofu', 'asparagus', 'ginger', 'cottage cheese', 'vegetable oil', 'peas', 'beef', 'garlic', 'black pepper', 'cream', 'vodka', 'paprika', 'beet', 'mushroom', 'pesto', 'cloves', 'spinach', 'basil', 'pickles', 'cucumber', 'pork', 'sweet potato', 'watermelon', 'onion', 'oregano', 'honey', 'barbecue sauce', 'olive', 'grape', 'mozzarella', 'sour cream', 'coconut milk', 'mayonnaise', 'bacon', 'thyme', 'red wine', 'provence herbs', 'white wine', 'avocado', 'radish', 'salami', 'jalapeño', 'worcestershire sauce', 'curry powder', 'pomegranate', 'flour', 'eggplant', 'vanilla', 'apple', 'bread', 'broccoli', 'soy sauce', 'whiskey', 'pita', 'baguette', 'pineapple', 'rice', 'feta', 'potato', 'cod', 'parsley', 'zucchini', 'ricotta', 'cabbage', 'milk', 'tomato', 'butter', 'banana', 'cocoa powder', 'mustard', 'sausage', 'starch', 'carrot', 'gouda', 'lemon', 'mango', 'horseradish', 'cream cheese', 'dill', 'baking soda', 'baking powder', 'raspberry', 'tuna', 'chocolate', 'peach', 'orange', 'kiwi', 'gingerbread spice', 'trout', 'pasta', 'salmon', 'lettuce', 'brie', 'cherry', 'prosciutto', 'pear', 'vinegar', 'olive oil', 'egg noodles', 'blue cheese', 'cilantro', 'nutmeg', 'tortillas', 'butternut squash', 'cauliflower', 'bay leaf', 'cantaloupe', 'celery', 'hot sauce', 'cumin', 'cheddar', 'lime', 'beer', 'cinnamon', 'rosemary', 'ketchup', 'scallions', 'parmesan', 'cheese', 'coconut', 'leek', 'chicken', 'sugar', 'water'

## 📊 Evaluation
### 🔍 **1. Metrics**
We evaluated the ingredient detection system using the following metrics:
- **Precision**: Measures how accurate our predictions are (i.e., how many of the detected ingredients are correct).  
- **Recall**: Measures how many of the ground-truth ingredients were detected.  
- **mAP (Mean Average Precision)**: This metric gives a comprehensive view of precision and recall across different IoU thresholds.  

---

### 📊 **Model Evaluation Results**

| **IoU Threshold** | **Precision** | **Recall** |
|-------------------|---------------|------------|
| **0.1**           | 0.7034        | 0.8465     |
| **0.5**           | 0.5937        | 0.7951     |
| **0.75**          | 0.4884        | 0.7091     |
| **0.9**           | 0.3992        | 0.5785     |

> **What does this mean?** At **IoU=0.1**, the system identifies 84.65% of the ingredients in the image, and 70.34% of them are correctly classified with an overlap of at least 10%. As the IoU threshold increases, precision decreases, but this is expected since stricter thresholds require more precise localization.

---

## 🍽️ **Recipe Recommendation System**

### **How it works:**
1️⃣ **Input**: User uploads an image of ingredients.  
2️⃣ **Detection**: YOLOv11m identifies the ingredients.  
3️⃣ **Classification**: Each detected ingredient is classified (e.g., "onion", "garlic").  
4️⃣ **Recipe Matching**: Ingredients are compared to recipes in the CSV or sent to **ChatGPT** for creative suggestions.  

---

## ⚙️ **How to Run It**

1️⃣ **Install dependencies**:  
```bash
conda env create -f environment.yaml --name new_env_name
```

2️⃣ **Run the pipeline**:  
Place your images in 📂: `project/classification_pipeline/images`

Run the command:  
```bash
python main.py
```

3️⃣ **View the classified images**:  
Classified images will be saved in 📂: `project/classification_pipeline/results/annotated_images`

---

## 📂 **File Structure**

```
project_root/
├── chatGPT_API/               # GPT API, requires .env file with API key
├── classification_pipeline/   
│   ├── clip_model_pipeline/   
│   ├── yolo_model_pipeline/  
├── ingredients_config/        
├── recipe_dataset/            # CSV dataset with recipes
├── utils/                     # Helper scripts
├── app.py                     # App for uploading images and classifying them
├── README.md                  # This README file
├── main.py                    # Main script to run the project
└── paths_config.yaml          # Configurable paths for images, models, and outputs
```

This structure helps users and developers understand where to find key components of the system.

---

## 🧪 **Future Work**
- **Ingredient Quantity**: Measure how much of each ingredient is present (not just "onion" but **"50g of onion"**).  
- **More Recipes**: Use an API like **Spoonacular** to get more recipe suggestions.  
- **Better Train Dataset**: Improve dataset quality, especially for packaged ingredient images.  

---

## 📘 **Final Thoughts**
This README is designed to help users, instructors, and collaborators understand how **Remi** works. It explains the purpose, methodology, and usage clearly, while also offering insights into how to run and evaluate the system. Let us know if you'd like any part refined or expanded.

References

YOLOv11: An Overview of the Key Architectural Enhancements. Retrieved from [https://arxiv.org/abs/2410.17725]

Radford, A., et al. (2021). Learning Transferable Visual Models From Natural Language Supervision. Retrieved from [https://arxiv.org/abs/2103.00020]


