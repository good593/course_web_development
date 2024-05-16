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
# [Data elements](https://docs.streamlit.io/develop/api-reference/data)
![alt text](./img/image.png)

---
## [dataframe](https://docs.streamlit.io/develop/api-reference/data/st.dataframe)
- 컬럼을 클릭하면, 컬럼 기준으로 데이터 정렬이 가능하다. 

---
### 단계1: show dataframe
```shell
streamlit run ex-01.py
```
![alt text](./img/image-1.png)

---
### 단계2: a Pandas Styler object to change the style of the rendered DataFrame
```shell
streamlit run ex-02.py
```
![alt text](./img/image-2.png)

---
### 단계3: column_config
```shell
streamlit run ex-03.py
```
![alt text](./img/image-3.png)

---
### 단계4: use_container_width
```shell
streamlit run ex-04.py
```
![alt text](./img/image-4.png)

---
## [table](https://docs.streamlit.io/develop/api-reference/data/st.table)
- DataFrame과는 다르게 interactive 한 UI 를 제공하지 않습니다.
- 즉, 컬럼 기준으로 데이터 정렬이 불가능하다. 

---
### 단계1: table
```shell
streamlit run ex-05.py
```
![alt text](./img/image-5.png)

---
### 단계2: element.add_rows
- Concatenate a dataframe to the bottom of the current one.
```shell
streamlit run ex-06.py
```
![alt text](./img/image-6.png)

---
### 단계3: add more data to a line chart
```shell
streamlit run ex-07.py
```
![alt text](./img/image-7.png)

---
## [Data editor](https://docs.streamlit.io/develop/api-reference/data/st.data_editor)
- The data editor widget allows you to edit dataframes and many other data structures in a table-like UI.

---
### 단계1: data editor
```shell
streamlit run ex-08.py
```
![w:800](./img/image-8.png)

---
### 단계2: add and delete rows by setting num_rows to "dynamic"
```shell
streamlit run ex-09.py
```
![w:800](./img/image-9.png)

---
### 단계3: disabled > 수정불가
```shell
streamlit run ex-10.py
```
![w:800](./img/image-10.png)

---
## [metric](https://docs.streamlit.io/develop/api-reference/data/st.metric)
- Display a metric in big bold font, with an optional indicator of how the metric changed.

---
```shell
streamlit run ex-11.py
```
![alt text](./img/image-11.png)

---
## [json](https://docs.streamlit.io/develop/api-reference/data/st.json)
- Display object or string as a pretty-printed JSON string.

---
```shell
streamlit run ex-12.py
```
![alt text](./img/image-12.png)

---
## [Column configuration](https://docs.streamlit.io/develop/api-reference/data/st.column_config)
- Streamlit에서 데이터 작업을 할 때 st.column_config클래스는 데이터 표시 및 상호 작용을 구성하는 강력한 도구입니다. 

![alt text](./img/image-13.png)

