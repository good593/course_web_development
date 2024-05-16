import streamlit as st

st.title('Metric')
st.metric(label="Temperature", value="70 °F", delta="1.2 °F")


col1, col2, col3 = st.columns(3)
col1.metric(label="Temperature", value="70 °F", delta="1.2 °F", delta_color="inverse")
col2.metric(label="Wind", value="9 mph", delta="-8%", delta_color="inverse")
col3.metric(label="Humidity", value="86%", delta="4%", delta_color="off")
