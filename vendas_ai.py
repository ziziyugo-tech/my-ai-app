import streamlit as st
import requests

# --- 1. BRANDING & UI SETTINGS ---
st.set_page_config(page_title="The Python Tutor", page_icon="🐍")

# This adds the logo and the new professional titles
st.logo("🐍", size="large") 
st.title("The Python Tutor")
st.subheader("I don't just fix your code—I teach you why it broke.")

# --- 2. SIDEBAR HELP ---
with st.sidebar:
    st.header("About This Tutor")
    st.write("""
    This app uses the **Qwen-2.5-32B** model to analyze your Python errors. 
    It is designed to help students in Portugal and beyond master coding!
    """)
    st.divider()
    st.info("Tip: Paste the exact error message you got from your terminal for better results.")

# --- 3. API SETUP ---
api_key = st.secrets["OPENROUTER_API_KEY"]

# --- 4. USER INTERFACE ---
user_input = st.text_area("Paste your messy or broken code here:", height=200)

if st.button("Fix & Explain My Code"):
    if not user_input.strip():
        st.warning("Please paste some code first!")
    else:
        with st.spinner("Analyzing your code..."):
            # We updated the 'content' below to tell the AI to be a TUTOR
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "qwen/qwen-2.5-coder-32b-instruct",
                    "messages": [
                        {
                            "role": "system", 
                            "content": "You are an expert Python Tutor. Provide the corrected code first, then provide a clear, bulleted explanation of what was wrong and how to avoid the mistake next time."
                        },
                        {
                            "role": "user", 
                            "content": f"Fix and explain this code: {user_input}"
                        }
                    ]
                }
            )
            
            result = response.json()
            
            # Displaying the result
            if 'choices' in result:
                answer = result['choices'][0]['message']['content']
                st.markdown(answer)
            else:
                st.error("Something went wrong with the AI connection. Check your API key!")