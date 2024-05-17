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
# [Input widgets](https://docs.streamlit.io/develop/api-reference/widgets)
- With widgets, Streamlit allows you to bake interactivity directly into your apps with buttons, sliders, text inputs, and more.

![alt text](./img/image.png)

---
## [Button elements](https://docs.streamlit.io/develop/api-reference/widgets#button-elements)

---
### 단계1: button 
```shell
streamlit run ex-01.py
```
![alt text](./img/image-1.png)

---
### 단계2: download button 
```shell
streamlit run ex-02.py
```
![alt text](./img/image-2.png)

---
### 단계3: [form button](https://blog.streamlit.io/introducing-submit-button-and-forms/) 
```shell
streamlit run ex-03.py
```
![alt text](./img/image-3.png)

---
### 단계4: link button 
```shell
streamlit run ex-04.py
```
![alt text](./img/image-4.png)

---
## [Multi Pages](https://docs.streamlit.io/develop/api-reference/widgets/st.page_link) 
- `pages 폴더`가 존재하면, 자동으로 Multi Page로 인식을 함 
```shell
your-repository/
├── pages/
│   ├── page-1.py
│   └── page-2.py
└── ex-05.py
```

---
```shell
streamlit run ex-05.py
```
![alt text](./img/image-5.png)

---
## [Selection elements](https://docs.streamlit.io/develop/api-reference/widgets#selection-elements)

---
### 단계1: checkbox 
```shell
streamlit run ex-06.py
```
![alt text](./img/image-6.png)

---
### 단계2: toggle 
```shell
streamlit run ex-07.py
```
![alt text](./img/image-7.png)

---
### 단계3: radio 
```shell
streamlit run ex-08.py
```
![alt text](./img/image-8.png)

---
### 단계4: radio > label_visibility
- Widgets can customize how to hide their labels with the `label_visibility` parameter.
```shell
streamlit run ex-09.py
```
![alt text](./img/image-9.png)

---
### 단계5: selectbox
```shell
streamlit run ex-10.py
```
![alt text](./img/image-10.png)

---
### 단계6: selectbox > label_visibility
```shell
streamlit run ex-11.py
```
![alt text](./img/image-11.png)

---
### 단계7: multiselect
```shell
streamlit run ex-12.py
```
![alt text](./img/image-12.png)

---
## [Numeric input elements](https://docs.streamlit.io/develop/api-reference/widgets#numeric-input-elements)

---
### 단계1: number_input
```shell
streamlit run ex-13.py
```
![w:800](./img/image-13.png)

---
### 단계2: slider
```shell
streamlit run ex-14.py
```
![w:800](./img/image-14.png)

---
## [Date and time input elements](https://docs.streamlit.io/develop/api-reference/widgets#date-and-time-input-elements)

---
### 단계1: date_input
```shell
streamlit run ex-15.py
```
![w:800](./img/image-15.png)

---
### 단계2: time_input
```shell
streamlit run ex-16.py
```
![w:800](./img/image-16.png)

---
## [Text input elements](https://docs.streamlit.io/develop/api-reference/widgets#text-input-elements)

---
### 단계1: text_input
```shell
streamlit run ex-17.py
```
![w:800](./img/image-17.png)

---
### 단계2: text_area
```shell
streamlit run ex-18.py
```
![w:800](./img/image-18.png)

---
### 단계3: chat_input
```shell
streamlit run ex-19.py
```
![w:800](./img/image-19.png)

---
## [Other input elements](https://docs.streamlit.io/develop/api-reference/widgets#other-input-elements)
![alt text](./img/image-20.png)



