---
style: |
  img {
    display: block;
    float: none;
    margin-left: auto;
    margin-right: auto;
  }
marp: true
paginate: true
---
# Groq를 이용한 Chatbot 예제 

- [Groq](https://groq.com/) 
  - Groq는 Python과 JavaScript/Typescript 클라이언트 라이브러리를 모두 제공합니다.
  - Groq Python 라이브러리는 Python 3.7 이상 애플리케이션에서 Groq REST API에 편리하게 액세스할 수 있도록 합니다.

---
## 가상환경
1. 챗봇 프로젝트 폴더로 이동
2. 가상환경 만들기
```shell 
uv venv .venv
```
3. 가상환경 접속
```shell 
.\.venv\Scripts\activate
```
4. 라이브러리 설치 
```shell
uv pip install -r .\requirements.txt
```

---
## 챗봇 실행 
1. `.env_sample`을 이용해서 `.env`파일 생성 
2. `.env`파일에 `OPENAI_API_KEY` 입력 
3. streamlit 실행 
```shell
streamlit run chatbot.py
```

