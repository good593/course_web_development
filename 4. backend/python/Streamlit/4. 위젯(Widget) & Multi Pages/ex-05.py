import streamlit as st

st.title('Multi Page Link')
st.page_link("./ex-05.py", label="Home", icon="🏠")
st.page_link("./pages/page-1.py", label="Page 1", icon="1️⃣")
st.page_link("./pages/page-2.py", label="Page 2", icon="2️⃣", disabled=True)
st.page_link("http://www.google.com", label="Google", icon="🌎")