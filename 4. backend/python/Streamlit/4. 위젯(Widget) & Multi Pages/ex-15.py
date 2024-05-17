import streamlit as st
import datetime

st.title('date_input')
d1 = st.date_input("When's your birthday", value=None)
st.write("Your birthday is:", d1)


today = datetime.datetime.now()
next_year = today.year + 1
jan_1 = datetime.date(next_year, 1, 1)
dec_31 = datetime.date(next_year, 12, 31)

d2 = st.date_input(
    "Select your vacation for next year",
    (jan_1, datetime.date(next_year, 1, 7)),
    jan_1,
    dec_31,
    format="MM.DD.YYYY",
)
st.write("your vacation:", d2)

