# Remi: Ingredient Classification and Recipe Recommendation System

## 📘 Introduction
**Remi** is an AI-powered system that classifies ingredients in an image and recommends recipes you can make with them. We leverage a combination of modern computer vision techniques like **YOLOv11** for ingredient detection and **CLIP-based classification** for more specific ingredient identification. The detected ingredients are matched against a **recipe database** to suggest dishes that can be prepared with the available ingredients or alternatively fed in to ChatGPT API.

The system is designed to provide fast, accurate, and practical suggestions for users looking for inspiration in the kitchen.

---

## 🚀 Features
- **Ingredient Detection**: Uses **YOLOv11m** to detect general ingredient objects from images.  
- **Ingredient Classification**: Crops detected objects and classifies them using **CLIP** embeddings and a custom label list.  
- **Recipe Suggestion**: Matches the identified ingredients against a recipe database to suggest dishes that require the available ingredients.  
- **Scalability**: Supports adding more datasets, labels, and custom recipes.  

---

## 📷 System Architecture / Workflow

---

## 📚 Methodology

### 🧑‍🔬 **1. Data Collection**
We sourced datasets for ingredients from various online sources, specifically from Roboflow and combined them into a **unified COCO-like format**. This allowed us to train YOLOv11 on a larger and more diverse set of ingredient images. We even added images that did not contained ingredients but packed products such as toothpastes due to lack of datasets containing packed labeled ingredients such as milk, spices etc. 

### ⚙️ **2. Object Detection with YOLOv11m**
We trained a **YOLOv11** model to detect general ingredient objects in images. The model detects bounding boxes for objects like "onion", "carrot", or "tomato".

**Training details**:
- **Datasets**: Combined datasets from multiple online sources.
- **Epochs**: XX epochs with **X batches**.
- **Augmentations**: Flips, color shifts, random noise, and others that were included in downloaded datasets

### 🖼️ **3. Ingredient Classification using CLIP**
After YOLOv11 detects objects, each detected object is **cropped** and passed into a **CLIP-based classification system**.

**Why CLIP?** CLIP can classify images based on text embeddings, so we created a list of custom **ingredient labels** like "tomato", "sweet potato", "beer", and so on. Each image crop is classified into one of these categories.

### 🍲 **4. Recipe Matching**
Once the ingredients are identified, they are matched against a **recipe database (CSV file)**. We filter recipes by checking if the detected ingredients are sufficient to create the recipe. If some ingredients are missing, the system informs the user which ingredients are required.

---

## 📊 Evaluation

### 🔍 **1. Metrics**

## 📊 Model Evaluation Results

### **Model 1**
| **IoU Threshold** | **Precision** | **Recall** |
|-------------------|---------------|------------|
| **0.1**           | 0.7034        | 0.7845     |
| **0.5**           | 0.5937        | 0.7321     |
| **0.75**          | 0.4884        | 0.6519     |
| **0.9**           | 0.3992        | 0.5373     |

### **Model 2**
| **IoU Threshold** | **Precision** | **Recall** |
|-------------------|---------------|------------|
| **0.1**           | 0.6709        | 0.8465     |
| **0.5**           | 0.5398        | 0.7951     |
| **0.75**          | 0.4252        | 0.7091     |
| **0.9**           | 0.3436        | 0.5785     |

---


## 🍽️ Recipe Recommendation System

### **How it works:**
1️⃣ **Input**: User uploads an image of ingredients.  
2️⃣ **Detection**: YOLOv11 identifies the ingredients.  
3️⃣ **Classification**: Each detected ingredient is classified (e.g., "onion", "garlic").  
4️⃣ **Recipe Matching**: Ingredients are compared to recipes in the CSV, and matching recipes are displayed.  

You can enhance this with a visual demo (like a GIF) or screenshots.

---

## ⚙️ How to Run It

1️⃣ **Install dependencies**:  
```bash
pip install -r requirements.txt
```

2️⃣ **Run the pipeline**:  
```bash
python main.py --image_path="test_image.jpg"
```

3️⃣ **Expected Output**:  
```
Detected Ingredients: onion, garlic, tomato
Suggested Recipes: Tomato Basil Soup, Pasta Primavera
```

---

## 📂 File Structure

```
project_root/
├── src/                   # Source code
│   ├── data/              # Data scripts for handling COCO files
│   ├── models/            # YOLOv11 and CLIP models
│   ├── visualization/     # Scripts for generating graphs/plots
├── data/                  # Data (datasets, CSVs, etc.)
├── notebooks/             # Jupyter notebooks for exploration
├── requirements.txt       # Python dependencies
├── README.md              # This README
└── main.py                # Main script for running everything
```

This structure helps users and developers understand where to find key components of the system.

---

## 🧪 Possible Improvements
- **Ingredient Quantity**: Measure how much of each ingredient is present (not just "onion" but **"50g of onion"**).  
- **Visual Feedback**: Show ingredient labels directly on the image.  
- **More Recipes**: Use an API like **Spoonacular** to get more recipe suggestions.  

---

## 📘 Final Thoughts
This README is designed to help users, instructors, and collaborators understand how **Remi** works. It explains the purpose, methodology, and usage clearly, while also offering insights into how to run and evaluate the system. If you need any part refined, feel free to reach out!

