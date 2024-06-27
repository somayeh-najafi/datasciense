import pandas as pd
import streamlit as st

uploaded_file = pd.read_csv('Projects/8-RegulatorySolution/Deployment/Streamlit/Test_Dataset_E100.csv')
st.write(uploaded_file)