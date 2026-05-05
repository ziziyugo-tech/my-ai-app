import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="AI Chat", layout="centered")
st.title("🧠 AI Chat Multi-Ficheiros")

api_key = st.secrets.get("OPENROUTER_API_KEY", "")

with st.sidebar:
    st.header("📎 Anexar")
    uploaded_file = st.file_uploader("Sobe PDF, Voz, Imagem...", 
                                    type=["pdf", "txt", "png", "jpg", "mp3", "mp4"])
    
# Função para converter imagem para texto (Base64)
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escreve aqui..."):
    # Se houver uma imagem, vamos anexá-la à mensagem
    conteudo_mensagem = [{"type": "text", "text": prompt}]
    
    if uploaded_file and uploaded_file.type in ["image/png", "image/jpeg"]:
        base64_image = encode_image(uploaded_file)
        conteudo_mensagem.append({
            "type": "image_url",
            "image_url": {"url": f"data:{uploaded_file.type};base64,{base64_image}"}
        })

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("A analisar..."):
        try:
            # Usamos o modelo 'google/gemini-2.0-flash-001' que é ótimo para imagens
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "google/gemini-2.0-flash-001", 
                    "messages": [{"role": "user", "content": conteudo_mensagem}]
                }
            )
            res = response.json()['choices'][0]['message']['content']
            with st.chat_message("assistant"):
                st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
        except:
            st.error("Erro ao processar o ficheiro. Verifica a API Key.")