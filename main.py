import streamlit as st
from purpose import purpose
from app import app

# Create a Streamlit app with tabs
st.sidebar.title("Navigation")
tabs = st.sidebar.radio("", ("Purpose", "App"))

if tabs == "Purpose":
    purpose()
elif tabs == "App":
    app()
