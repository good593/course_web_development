import streamlit as st
import datetime

st.title('time_input')
t1 = st.time_input("Set an alarm for", datetime.time(8, 45))
st.write("Alarm is set for", t1)

t2 = st.time_input("Set an alarm for", value=None)
st.write("Alarm is set for", t2)
