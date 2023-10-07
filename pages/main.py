import streamlit as st
from purpose import purpose
from pages.app import app

def purpose_page():
    st.markdown("# Purpose 🤔")
    purpose()

def app_page():
    st.markdown("# App 👂")
    app()

page_names_to_funcs = {
    "Purpose 🤔": purpose_page,
    "App 👂": app_page,
}

st.sidebar.title("Navigation")
selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()
