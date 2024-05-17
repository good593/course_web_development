import streamlit as st
import pandas as pd
import numpy as np

chart_data = pd.DataFrame(
    {"col1": list(range(20)), "col2": np.random.randn(20), "col3": np.random.randn(20)}
)
st.dataframe(chart_data[:2]) 
st.bar_chart(
    chart_data, x="col1", y=["col2", "col3"], color=["#FF0000", "#0000FF"]  # Optional
)