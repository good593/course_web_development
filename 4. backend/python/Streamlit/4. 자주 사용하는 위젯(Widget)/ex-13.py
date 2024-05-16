import streamlit as st

st.title('number input')
number1 = st.number_input("Insert a number")
st.write("The current number is ", number1)


number2 = st.number_input("Insert a number", value=None, placeholder="Type a number...")
st.write("The current number is ", number2)

