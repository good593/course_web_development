import time
import streamlit as st

from groq import Groq # API 통신용 모듈 
from .constant import CHATBOT_ROLE, CHATBOT_MESSAGE

# @st.cache_data # 데이터를 caching 처리 
@st.cache_resource # 객체를 caching 처리 
def get_client():
    return Groq()

def response_from_llm(prompt, message_history=None, model_id:str="gemma2-9b-it"):
    messages = [
        {
            CHATBOT_MESSAGE.role.name: CHATBOT_ROLE.assistant.name, 
            CHATBOT_MESSAGE.content.name: "You are a helpful assistant. You must answer in Korean.",
        }
    ]

    if isinstance(message_history, list):
        messages += message_history

    # 사용자 질문 추가
    messages.append(
        {
            CHATBOT_MESSAGE.role.name: CHATBOT_ROLE.user.name,
            CHATBOT_MESSAGE.content.name: prompt,
        },
    )

    streaming = get_client().chat.completions.create(
        model=model_id,
        messages=messages,
        stream=True
    )

    # return streaming.choices[0].message.content
    for chunk in streaming:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content
            time.sleep(0.05)


