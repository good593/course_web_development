import streamlit as st

# Using object notation
add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone")
)

# Using "with" notation
with st.sidebar:
    add_radio = st.radio(
        "Choose a shipping method",
        ("Standard (5-15 days)", "Express (2-5 days)")
    )
    
if add_selectbox:
    st.subheader("selectbox")
    st.text(add_selectbox)
    
if add_radio:
    st.subheader("radio")
    st.text(add_radio)