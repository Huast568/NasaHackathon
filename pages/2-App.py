import streamlit as st
import cv2
import numpy as np


st.title("Image and Video Sonification")

# Choose between image or video using radio buttons
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

elif file_type == "Video":
    # Upload video file
    uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])

    if uploaded_file is not None:
        # Display the uploaded video
        st.video(uploaded_file, format="video/mp4")

        # You can save the uploaded video file to a variable if needed
        video_bytes = uploaded_file.read()
        st.write("Video file size:", len(video_bytes), "bytes")