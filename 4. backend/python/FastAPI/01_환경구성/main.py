from fastapi import FastAPI

app = FastAPI(
    title="My First API",
    description="FastAPI 입문 강의 실습",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/hello/{name}")
def hello(name: str):
    return {"message": f"안녕하세요, {name}님!"}


@app.get("/info")
def get_info():
    return {
        "framework": "FastAPI",
        "language": "Python",
        "docs_url": "/docs",
    }
