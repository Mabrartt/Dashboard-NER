import streamlit as st
import Home
import Visualize

# Set up the tabs
st.title("NER Dashboard for SEAWEED and LOCATION")
tabs = st.tabs(["Home", "Visualize"])

# Render the content for each tab
with tabs[0]:
    Home.render_home()

with tabs[1]:
    Visualize.render_visualize()
