"""
Streamlit으로 만든 챗봇 화면입니다.

흐름:
1. 사용자가 메시지를 입력합니다.
2. Streamlit이 FastAPI의 `/chat/stream`으로 요청합니다.
3. FastAPI가 Groq 답변 조각을 SSE로 보내면 화면에 실시간으로 출력합니다.
"""

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
    # Streamlit은 버튼이나 입력이 바뀔 때마다 파일을 위에서부터 다시 실행합니다.
    # 그래서 대화 기록처럼 유지해야 하는 값은 session_state에 저장합니다.
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = DEFAULT_API_BASE_URL


init_state()

with st.sidebar:
    # 사이드바는 서버 주소와 모델 파라미터를 조정하는 설정 영역입니다.
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
        # 화면과 모델에 전달할 이전 대화 기록을 모두 비웁니다.
        st.session_state.messages = []
        st.rerun()

# 저장된 대화 기록을 화면에 다시 그립니다.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("메시지를 입력하세요")

if prompt:
    # 현재 질문을 기록에 추가하기 전에 복사해 두어야, 백엔드에는 "이전 대화"만 전달됩니다.
    history = st.session_state.messages.copy()
    user_message = create_message("user", prompt)
    if user_message is None:
        st.stop()

    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # stream_answer는 토큰을 하나씩 yield하고, st.write_stream은 그것을 화면에 이어 씁니다.
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

    # 완성된 답변을 session_state에 저장해야 다음 질문 때 history로 함께 보낼 수 있습니다.
    assistant_message = create_message("assistant", answer)
    if assistant_message:
        st.session_state.messages.append(assistant_message)
