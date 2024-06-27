import pandas as pd
import streamlit as st

uploaded_file = pd.read_csv('Projects/8-RegulatorySolution/Deployment/Streamlit/Test_Dataset_E100.csv')
uploaded_file=uploaded_file.fillna('None')
st.write(uploaded_file)