"""
생성형 AI를 활용한 API 문서 자동화

실행 전 .env 파일에 GROQ_API_KEY를 설정하고,
api_server.py FastAPI 서버를 먼저 실행하세요.

사용법:
  python main.py pipeline    # 전체 파이프라인 (문서 + Collection + README)
  python main.py docs        # 마크다운 API 문서만
  python main.py collection  # Postman Collection만
  python main.py readme      # README만
  python main.py diff        # 이전 스펙과 비교해 변경분만 업데이트
"""
from cli import main


if __name__ == "__main__":
    main()
