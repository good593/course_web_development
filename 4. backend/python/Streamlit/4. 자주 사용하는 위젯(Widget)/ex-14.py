import streamlit as st
from datetime import datetime

st.title('slider')
age = st.slider("How old are you?", 0, 130, 25)
st.write("I'm ", age, "years old")

values = st.slider(
    "Select a range of values",
    0.0, 100.0, (25.0, 75.0))
st.write("Values:", values)

start_time = st.slider(
    "When do you start?",
    value=datetime(2020, 1, 1, 9, 30),
    format="MM/DD/YY - hh:mm")
st.write("Start time:", start_time)
