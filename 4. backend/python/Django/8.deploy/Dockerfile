FROM python:3.12

# 로컬의 django_server 폴더를 컨테이너의 /app 폴더로 복사합니다.
COPY ./django_server /app

# entrypoint.sh 스크립트를 컨테이너의 /app/entrypoint.sh로 복사합니다.
COPY ./entrypoint.sh /app/entrypoint.sh

# 작업 디렉토리를 /app으로 설정합니다.
WORKDIR /app

# pip을 최신 버전으로 업그레이드하고,
# requirements.txt에 명시된 패키지를 설치합니다.
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

# 컨테이너가 시작될 때 entrypoint.sh를 실행합니다.
ENTRYPOINT [ "sh", "/app/entrypoint.sh" ]
