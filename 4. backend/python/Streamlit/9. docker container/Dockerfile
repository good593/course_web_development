# Base 이미지
FROM python:3.12-slim

# 작업 디렉토리 설정
WORKDIR /app


# 소스 복사 
COPY lotto.py requirements.txt /app/

# 라이브러리 설치 
RUN pip3 install -r requirements.txt

# 포트 오픈 
EXPOSE 8501

# 컨테이너 헬스 체크
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# 애플리케이션 실행 
ENTRYPOINT ["streamlit", "run", "lotto.py", "--server.port=8501", "--server.address=0.0.0.0"]