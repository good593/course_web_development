import streamlit as st

conn = st.connection("mydb", type="sql", autocommit=True)

df = conn.query("show databases", ttl=3600)
st.dataframe(df)
