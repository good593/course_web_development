import streamlit as st
import pandas as pd

# 파일 다운로드 버튼
# 샘플 데이터 생성
dataframe = pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40],
})

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

st.title('Download file')
st.dataframe(dataframe)

# 다운로드 버튼 연결
st.download_button(
    label='Download data as CSV',
    data=convert_df(dataframe), 
    file_name='sample.csv', 
    mime='text/csv'
)
