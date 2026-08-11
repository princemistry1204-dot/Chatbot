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
    Load and cache the trained Keras vehicle and fruit classification models.
    """
    vehicle_model = None
    fruit_model = None

    if os.path.exists(vehicle_model_path):
        try:
            vehicle_model = tf.keras.models.load_model(vehicle_model_path)
        except Exception:
            pass

    if os.path.exists(fruit_model_path):
        try:
            fruit_model = tf.keras.models.load_model(fruit_model_path)
        except Exception:
            pass

    return vehicle_model, fruit_model  


def ask_image(file_path: str, question: str = ""):
    """
    Classifies an image using the loaded model(s) and returns the prediction result.
    Auto-selects higher confidence model if question doesn't specify category.
    """
    question_lower = (question or "").lower()
    vehicle_model, fruit_model = load_model()

    if vehicle_model is None and fruit_model is None:
        return "Error: Image classification models could not be loaded."

    img = cv2.imread(file_path)
    if img is None:
        return "Error: Unable to load or read the uploaded image file."

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (128, 128))
    st.image(img_rgb, caption="Uploaded Image", use_container_width=True)

    img_array = tf.keras.utils.img_to_array(img_resized)
    img_array = tf.expand_dims(img_array, 0)

    def predict_with_model(model, labels):
        if model is None:
            return None, 0.0
        prediction = model.predict(img_array)
        score = tf.nn.softmax(prediction[0])
        idx = int(np.argmax(score))
        conf = float(np.max(score))
        label = labels[idx] if idx < len(labels) else f"Class_{idx}"
        return label, conf

    category = None
    predicted_label = None
    confidence = 0.0

    if "vehicle" in question_lower and vehicle_model is not None:
        predicted_label, confidence = predict_with_model(vehicle_model, VEHICLE_NAMES)
        category = "Vehicle"
    elif "fruit" in question_lower and fruit_model is not None:
        predicted_label, confidence = predict_with_model(fruit_model, FRUIT_NAMES)
        category = "Fruit"
    else:
        # Auto-detect between vehicle and fruit model based on higher confidence score
        v_label, v_conf = predict_with_model(vehicle_model, VEHICLE_NAMES)
        f_label, f_conf = predict_with_model(fruit_model, FRUIT_NAMES)

        if v_conf >= f_conf and v_label is not None:
            predicted_label, confidence = v_label, v_conf
            category = "Vehicle"
        else:
            predicted_label, confidence = f_label, f_conf
            category = "Fruit"

    st.write(f"**Prediction ({category}):** {predicted_label} ({confidence:.1%} confidence)")

    return f"Image Prediction ({category}): {predicted_label} (Confidence: {confidence:.1%})"