import streamlit as st

# Header 적용
st.header('헤더를 입력할 수 있어요! :sparkles:')

# 코드 표시
sample_code = '''
def function():
    print('hello, world')
'''
st.code(sample_code, language="python")

# 일반 텍스트
st.text('일반적인 텍스트를 입력해 보았습니다.')

