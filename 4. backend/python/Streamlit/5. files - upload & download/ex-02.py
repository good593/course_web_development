import streamlit as st
import pandas as pd

st.title('Upload file')
uploaded_files = st.file_uploader("Choose a CSV or excel file",  accept_multiple_files=True, type=['csv', 'xls', 'xlsx'])

for file in uploaded_files:
    st.write("filename:", file.name)

    if file is not None:
        ext = file.name.split('.')[-1]
        if ext == 'csv':
            # 파일 읽기
            df = pd.read_csv(file)
            # 출력
            st.dataframe(df)
        elif 'xls' in ext:
            # 엑셀 로드
            df = pd.read_excel(file, engine='openpyxl')
            # 출력
            st.dataframe(df)
