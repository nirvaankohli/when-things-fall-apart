import streamlit as st

st.set_page_config(
    page_title="Twitter Sentiment Analysis", layout="wide", page_icon="🐦"
)


def home_page():

    st.title("Twitter Profile Sentiment Analysis App")



def about_page():

    st.title("How it works: Behind The Scenes")

    try:

        with open("bts.md", "r", encoding="utf-8") as file:
            
            content = file.read()
        
        st.markdown(content)
    
    except FileNotFoundError:
        
        st.error("bts.md file not found")


home = st.Page(home_page, title="Home(Demo)", icon="🐦")
about = st.Page(about_page, title="How it works: Behind The Scenes", icon="📃")

pg = st.navigation([home, about])
pg.run()
