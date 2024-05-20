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
### 단계1: lotto.py 확인 
```shell
streamlit run lotto.py
```
![alt text](./img/image.png)

---
### 단계2: [도커파일 생성](https://docs.streamlit.io/deploy/tutorials/docker)
- 참고문서: `Dockerfile`

![alt text](./img/image-1.png)

---
### 단계3: [Build a Docker image](https://docs.streamlit.io/deploy/tutorials/docker#build-a-docker-image) 
```shell
docker build -t streamlit .
docker images
```
![alt text](./img/image-2.png)

---
### 단계4: [Run the Docker container](https://docs.streamlit.io/deploy/tutorials/docker#run-the-docker-container) 
```shell
docker run --name streamlit-container -d -p 8501:8501 streamlit
docker ps
```
![alt text](./img/image-3.png)

---
### 단계5: 접속 > http://localhost:8501
![alt text](./img/image-4.png)
