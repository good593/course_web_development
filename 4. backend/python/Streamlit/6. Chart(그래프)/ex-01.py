import streamlit as st
import pandas as pd
import numpy as np

chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
st.dataframe(chart_data[:2]) 
st.area_chart(chart_data)