import tensorflow as tf
import numpy as np
from PIL import Image
import io
import pandas as pd

# 1. Dataset loading
try:
    df = pd.read_csv('indian_food.csv')
except FileNotFoundError:
    df = pd.read_csv('indian_food_dataset.csv')

# 2. Models load karein (Dono models ka ensemble accuracy badhayega)
try:
    m1 = tf.keras.models.load_model('model_mobilenet.h5')
    m2 = tf.keras.models.load_model('model_inception.h5') # InceptionV3 patterns ke liye best hai
except Exception as e:
    print(f"Error loading models: {e}. Make sure .h5 files exist.")

# 3. Classes load karein
with open('classes.txt', 'r') as f:
    class_names = [line.strip() for line in f.readlines()]

def predict_image(image_bytes):
    # Image preprocessing
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB').resize((224, 224))
    img_arr = np.array(img) / 255.0
    img_arr = np.expand_dims(img_arr, axis=0)

    # 4. Ensemble Prediction (Dono models se result lein)
    p1 = m1.predict(img_arr)
    p2 = m2.predict(img_arr)
    
    # Dono predictions ka average nikalna accuracy badhata hai
    combined = (p1 + p2) / 2
    
    idx = np.argmax(combined[0])
    dish_name = class_names[idx].replace("_", " ")
    
    # 5. Real AI Confidence (Aapka random logic hata diya hai)
    conf_score = np.max(combined[0]) * 100
    conf = f"{conf_score:.2f}%"

    # 6. CSV Search Logic
    res = df[df['name'].str.lower() == dish_name.lower()]
    
    nut_dict = {}
    ingredients_str = "Ingredients info not available."
    description_str = "No extra description found."

    if not res.empty:
        data = res.iloc[0]
        # Basic Info
        ingredients_str = data.get('ingredients', 'N/A')
        description_str = (
            f"🍽️ Course: {data.get('course', 'N/A')} | "
            f"🌱 Diet: {data.get('diet', 'N/A')} | "
            f"📍 State: {data.get('state', 'N/A')} ({data.get('region', 'N/A')})"
        )

        # 7. Nutritional Mapping (Sugar aur Fiber fix kiya gaya hai)
        # Note: Agar CSV mein column ka naam alag hai toh yahan change karein
        nut_dict = {
            "calories": data.get('calories_kcal', 0),
            "protein": data.get('protein_g', 0),
            "carbs": data.get('carbs_g', 0),
            "fat": data.get('fat_g', 0),
            "sugar": data.get('sugar_g', 0),   # ✅ Fixed
            "fiber": data.get('fiber_g', 0),   # ✅ Fixed
            "calcium": data.get('calcium_mg', 0),
            "iron": data.get('iron_mg', 0)
        }
    else:
        # Default values agar CSV mein data na mile
        nut_dict = {
            "calories": 0, "protein": 0, "carbs": 0, 
            "fat": 0, "sugar": 0, "fiber": 0
        }

    return dish_name.title(), ingredients_str, description_str, conf, nut_dict