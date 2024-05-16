import streamlit as st

st.title('Checkbox')
agree = st.checkbox("I agree")

if agree:
    st.write("Great!")
