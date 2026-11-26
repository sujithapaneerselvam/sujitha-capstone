import json,requests
import streamlit as st
from agent import SIMPLE,MULTI
api="http://127.0.0.1:8017"
st.title("BrightPath approval demo")
st.caption("Local fixture; no real emails are sent.")
q=st.selectbox("Example request",[SIMPLE,MULTI])
try:
    if st.button("Run request"):
        with requests.get(api+"/ask",params={"q":q},stream=True,timeout=20) as r:
            r.raise_for_status()
            for line in r.iter_lines(chunk_size=1):
                if line: st.write(json.loads(line))
    st.subheader("Pending approvals")
    for row in requests.get(api+"/pending",timeout=5).json():
        st.json(json.loads(row["args"]))
        for choice in ("approve","reject"):
            if st.button(choice.title(),key=row["id"]+choice):
                r=requests.post(api+"/approve",json={"id":row["id"],"decision":choice},timeout=5)
                r.raise_for_status()
                st.rerun()
    st.subheader("Audit trail")
    st.dataframe(requests.get(api+"/audit",timeout=5).json())
except requests.RequestException as e: st.error(str(e))
