import streamlit as st

from common.api_client import health_check, stream_answer
from common.config import (
    DEFAULT_API_BASE_URL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    PAGE_TITLE,
)
from common.message import create_message

st.set_page_config(page_title=PAGE_TITLE)
st.title(PAGE_TITLE)


def init_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = DEFAULT_API_BASE_URL


init_state()

with st.sidebar:
    st.header("API 설정")
    st.session_state.api_base_url = st.text_input(
        "FastAPI URL",
        value=st.session_state.api_base_url,
    )
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=2.0,
        value=DEFAULT_TEMPERATURE,
        step=0.1,
    )
    max_tokens = st.slider(
        "Max tokens",
        min_value=100,
        max_value=4096,
        value=DEFAULT_MAX_TOKENS,
        step=100,
    )

    if st.button("FastAPI 상태 확인"):
        try:
            status = health_check(st.session_state.api_base_url)
        except Exception as exc:
            st.sidebar.error(f"FastAPI 연결 실패: {exc}")
        else:
            st.sidebar.success("FastAPI 연결 성공")
            st.sidebar.json(status)

    if st.button("대화 초기화"):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("메시지를 입력하세요")

if prompt:
    history = st.session_state.messages.copy()
    user_message = create_message("user", prompt)
    if user_message is None:
        st.stop()

    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(
                stream_answer(
                    api_base_url=st.session_state.api_base_url,
                    prompt=prompt,
                    history=history,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            )
        except Exception as exc:
            answer = f"오류가 발생했습니다: {exc}"
            st.error(answer)

    assistant_message = create_message("assistant", answer)
    if assistant_message:
        st.session_state.messages.append(assistant_message)
