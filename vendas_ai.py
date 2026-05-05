import streamlit as st
import requests

# 1. Configuração da Página - Focada no Chat
st.set_page_config(page_title="AI Multi-Tool Chat", page_icon="🧠", layout="centered")

st.title("🧠 AI Multi-Tool Chat")
st.info("Podes enviar mensagens ou anexar ficheiros (PDF, Áudio, Imagem) na barra lateral.")

# 2. Chave da API
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

# 3. BARRA LATERAL (Para os ficheiros que queres que a IA "leia")
with st.sidebar:
    st.header("📎 Anexar Conteúdo")
    uploaded_file = st.file_uploader("Sobe ficheiros (PDF, MP3, etc.)", 
                                    type=["pdf", "txt", "png", "jpg", "mp3", "mp4"])
    youtube_url = st.text_input("🔗 Link do YouTube")
    
    contexto_ficheiro = ""
    if uploaded_file:
        st.success(f"Lido: {uploaded_file.name}")
        # Placeholder para a extração real de conteúdo
        contexto_ficheiro = f"\n[Anexo: {uploaded_file.name}]"
    if youtube_url:
        contexto_ficheiro += f"\n[Link YouTube: {youtube_url}]"

# 4. MEMÓRIA DO CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. INPUT DO CHAT (A tua Chat Box)
if prompt := st.chat_input("Diz qualquer coisa..."):
    # Adicionar o contexto do ficheiro/link à pergunta
    prompt_completo = f"{prompt} {contexto_ficheiro}"
    
    # Mostrar a mensagem do utilizador
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Resposta da IA
    with st.spinner("A processar..."):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "qwen/qwen-2.5-coder-32b-instruct",
                    "messages": st.session_state.messages + [{"role": "user", "content": f"Contexto extra: {contexto_ficheiro}"}]
                }
            )
            answer = response.json()['choices'][0]['message']['content']
            
            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except:
            st.error("Erro na API. Verifica se configuraste a chave nos Secrets.")