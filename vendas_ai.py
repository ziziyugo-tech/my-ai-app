import streamlit as st
import requests

st.set_page_config(page_title="AI Chat", layout="centered")
st.title("🧠 AI Chat Multi-Ficheiros")

# Chave que está no site (Secrets)
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

# Barra lateral para os ficheiros
with st.sidebar:
    st.header("📎 Anexar")
    uploaded_file = st.file_uploader("Sobe PDF, Voz, Imagem...", 
                                    type=["pdf", "txt", "png", "jpg", "mp3", "mp4"])
    yt_url = st.text_input("🔗 Link do YouTube")

# Histórico das mensagens
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Caixa de Chat
if prompt := st.chat_input("Escreve aqui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Resposta da IA
    with st.spinner("A responder..."):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "qwen/qwen-2.5-coder-32b-instruct",
                    "messages": st.session_state.messages
                }
            )
            res = response.json()['choices'][0]['message']['content']
            with st.chat_message("assistant"):
                st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
        except:
            st.error("Erro. Verifica se a tua API KEY está bem posta no site.")DDD