import cv2
import numpy as np
import tensorflow as tf
import keras
import kagglehub
import streamlit as st
import os

def ask_image(file_path: str , question: str):
    with st.spinner("Image Loading..."):
                    model = tf.keras.models.load_model("Fruit_Image_Classification_model.keras")
    # ============================================================
    # IMAGE MODEL DATA (fruit classifier)
    # ============================================================
    kaggle_dataset = kagglehub.dataset_download(
    "karimabdulnabi/fruit-classification10-class"
    )
    print("Dataset Downloaded Successfully...")

    path = os.path.join(kaggle_dataset, "MY_data", "train")

    train_dataset = tf.keras.utils.image_dataset_from_directory(
        path,
        validation_split=0.2,
        subset="training",
        seed=100,
        image_size=(128, 128),
        batch_size=64,
    )


    img = cv2.imread(file_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (128, 128))
    st.image(img_rgb, caption="Uploaded Image")

    img_array = keras.utils.img_to_array(img_resized)
    img_array = tf.expand_dims(img_array, 0)

    prediction = model.predict(img_array)
    score = tf.nn.softmax(prediction[0])
    predicted_index = np.argmax(score)
    confidence = float(np.max(score))

    predicted_label = train_dataset.class_names[predicted_index]
    img = f"Fruit detected: {predicted_label} (confidence: {confidence:.1%})"

    st.write(f"**Prediction:** {predicted_label} ({confidence:.1%} confidence)")
    
    if not predicted_label:
        return "No fruit detected in the image."