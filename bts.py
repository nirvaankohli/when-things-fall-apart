import streamlit as st

st.title("How it works: Behind The Scenes")

with open("bts.md", "r", encoding="utf-8") as file:
    content = file.read()

st.markdown(content)
