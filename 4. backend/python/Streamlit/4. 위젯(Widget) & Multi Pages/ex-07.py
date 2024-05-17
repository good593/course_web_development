import streamlit as st

st.title('Toggle')
on = st.toggle("Activate feature")

if on:
    st.write("Feature activated!")
