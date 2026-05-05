import streamlit as st
import requests
import os

st.title("My Premium AI Coder")
st.write("Welcome! This app uses Qwen-32B to fix your code.")

# Get the key from the environment
api_key = os.getenv("OPENROUTER_API_KEY")

user_input = st.text_area("Paste your messy code here:")

if st.button("Fix My Code"):
    if not api_key:
        st.error("API Key not found! Run the PowerShell command again.")
    else:
        with st.spinner("Thinking..."):
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "qwen/qwen-2.5-coder-32b-instruct",
                    "messages": [{"role": "user", "content": f"Fix this code: {user_input}"}]
                }
            )
            result = response.json()
            st.code(result['choices'][0]['message']['content'])