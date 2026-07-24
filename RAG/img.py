import os
import cv2
import numpy as np
import tensorflow as tf
import streamlit as st
from labels.fruit_labels import fruit_label
CLASS_NAMES = fruit_label()

@st.cache_resource
def load_fruit_model():
    """
    Load and cache the trained Keras fruit classification model.
    """
    model_path = os.path.join(os.path.dirname(__file__), "Fruit_Image_Classification_model.keras")
    if os.path.exists(model_path):
        return tf.keras.models.load_model(model_path)
    return None


def ask_image(file_path: str, question: str = ""):
    """
    Classifies an image using the loaded model and returns the prediction result.
    """
    model = load_fruit_model()
    if model is None:
        return "Error: Fruit classification model file ('Fruit_Image_Classification_model.keras') not found."

    img = cv2.imread(file_path)
    if img is None:
        return "Error: Unable to load or read the uploaded image."

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (128, 128))
    st.image(img_rgb, caption="Uploaded Image", use_container_width=True)

    img_array = tf.keras.utils.img_to_array(img_resized)
    img_array = tf.expand_dims(img_array, 0)

    prediction = model.predict(img_array)
    score = tf.nn.softmax(prediction[0])
    predicted_index = int(np.argmax(score))
    confidence = float(np.max(score))

    predicted_label = CLASS_NAMES[predicted_index]
    st.write(f"**Prediction:** {predicted_label} ({confidence:.1%} confidence)")

    return f"Image Prediction: {predicted_label} (Confidence: {confidence:.1%})"
