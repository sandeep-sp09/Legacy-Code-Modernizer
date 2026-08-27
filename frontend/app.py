"""
Streamlit frontend (placeholder). Replace with app.jsx etc. if using React instead.
"""

import streamlit as st

st.title("Legacy Code Modernizer")

uploaded_file = st.file_uploader("Upload Pascal/C source file", type=["pas", "c"])

if uploaded_file:
    st.write("TODO: send file to backend /upload endpoint")
    st.write("TODO: trigger /process and poll for results")
    st.write("TODO: render dependency graph")
    st.write("TODO: render diff view (original vs generated C++)")
