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
# [Installation](https://docs.streamlit.io/get-started/installation)

---
### 단계1: 가상환경 생성하기 
```shell
python -m venv .venv # 가상환경 생성 
.\.venv\Scripts\activate # 가상환경 접속 
pip install --upgrade pip # upgrade
```
![alt text](./img/image.png)

---
### 단계2: Install Streamlit
```shell
pip install streamlit pandas numpy matplotlib seaborn finance-datareader
```
![alt text](./img/image-1.png)

---
### 단계3: Validate the installation by running our Hello app
```shell
streamlit hello
```
![alt text](./img/image-2.png)

---
- Plotting Demo

![alt text](./img/image-3.png)

---
- Mapping Demo

![alt text](./img/image-4.png)

---
- DataFrame Demo

![alt text](./img/image-5.png)

---
### 단계4: Stop server
- 명령어(시간이 좀 걸림): `ctrl + c` 

![alt text](./img/image-6.png)


