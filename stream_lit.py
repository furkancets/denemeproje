import streamlit as st 
import json 
import requests

st.title("Electric Consumption Calculator")
# taking user inputs
option = st.selectbox('What prediction time You want to perform?',('a days', 'five days'))
st.write("")
st.write("Select the numbers from slider below &")
x = st.text("X")
y = st.text("y")
#converting the inputs into a json format
inputs = {"operation": option,"X": x, "y": y}
# when the user clicks on button it will fetch the API
if st.button('Calculate'):
    res = requests.post(url = "http://localhost:8002/electric/prediction/fivedays", data = json.dumps (inputs))
    st.subheader (f"Response from API = {res.text}")