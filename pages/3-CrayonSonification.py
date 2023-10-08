import streamlit as st
import cv2
import numpy as np


st.title("Space Drawing Sonification")
st.write("Please select what type of file you would like to get music created for, and then upload an image or video of space.")

file_type = st.selectbox("Select file type:", ("Image", "Video"))

if file_type == "Image":
    # Upload image file
    uploaded_file = st.file_uploader("Upload an image file", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        # Display the uploaded image
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

        # Read the uploaded image using OpenCV
        image_bytes = uploaded_file.read()
        image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), 1)

        # You can now work with the 'image' variable as a NumPy array
        st.write("Image shape:", image.shape)

