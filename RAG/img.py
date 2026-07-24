import os
import cv2
import numpy as np
import tensorflow as tf
import streamlit as st

from labels.fruit_labels import fruit_label
from labels.vehicle_labels import vehicle_labels
VEHICLE_NAMES = vehicle_labels()
FRUIT_NAMES = fruit_label()


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
vehicle_model_path = os.path.join(
    BASE_DIR,
    "models",
    "Vehicle_Image_Classification_model.keras"
)
fruit_model_path = os.path.join(
    BASE_DIR,
    "models",
    "Fruit_Image_Classification_model.keras"
)
@st.cache_resource
def load_model():
    """
    Load and cache the trained Keras fruit classification model.
    """
    vehicle_model = tf.keras.models.load_model(vehicle_model_path)
    fruit_model = tf.keras.models.load_model(fruit_model_path)

    return vehicle_model, fruit_model  

def ask_image(file_path: str, question: str):
    """
    Classifies an image using the loaded model and returns the prediction result.
    """

    question = question.lower()
    vehicle_model, fruit_model = load_model()
    model = None
    CLASS_NAMES = None
    models = {
        "vehicle" : vehicle_model,
        "fruit" : fruit_model
    }
    
    if "vehicle" in question:
        model = models["vehicle"]
        CLASS_NAMES = VEHICLE_NAMES
    elif "fruit" in question:
        model = models["fruit"]
        CLASS_NAMES = FRUIT_NAMES
    else:
        return "Error: Invalid question. Please specify 'vehicle' or 'fruit' in your question."
    
    img = cv2.imread(file_path)
    if img is None:
        return "Error: Unable to load or read the uploaded image."

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (128, 128))
    st.image(img_rgb, caption="Uploaded Image")

    img_array = tf.keras.utils.img_to_array(img_resized)
    img_array = tf.expand_dims(img_array, 0)

    prediction = model.predict(img_array)
    score = tf.nn.softmax(prediction[0])
    predicted_index = int(np.argmax(score))
    confidence = float(np.max(score))

    predicted_label = CLASS_NAMES[predicted_index]
    st.write(f"**Prediction:** {predicted_label} ({confidence:.1%} confidence)")

    return f"Image Prediction: {predicted_label} (Confidence: {confidence:.1%})"