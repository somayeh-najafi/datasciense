# app.py
import streamlit as st
from inspection import inspection
from compliance import compliance
from utils import home_page, licensing_section, compliance_section, chatbot_section

# Set page configuration
st.set_page_config(layout="wide")

# Main app page
def main():
    home_page()

# Page routing
def page_router():
    pages = {
        "Home": main,
        "Inspection": inspection,
        "Licensing": licensing_section,
        "Compliance": compliance_section,
        "Chatbot": chatbot_section
    }

    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", list(pages.keys()))
    pages[page]()

# Run the page router
if __name__ == "__main__":
    page_router()
