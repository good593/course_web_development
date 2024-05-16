import streamlit as st
import pandas as pd

st.title('Submit Button')
# Using the "with" syntax
with st.form(key='my_form'):
	text_input = st.text_input(label='Enter some text')
	submit_button = st.form_submit_button(label='Submit')

st.write('Press submit to have your name printed below')

if submit_button:
    st.write(f'hello {text_input}')