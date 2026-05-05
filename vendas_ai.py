import streamlit as st
import requests

# Configuração da página
st.set_page_config(page_title="AI Tutor", page_icon="🤖")

st.title("🤖 AI Tutor")

# Chave de API lida dos Secrets
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

# Memória do chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar histórico
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input do utilizador
if prompt := st.chat_input("Como posso ajudar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chamada à API do OpenRouter
    with st.spinner("A pensar..."):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "qwen/qwen-2.5-coder-32b-instruct",
                    "messages": st.session_state.messages
                }
            )
            answer = response.json()['choices'][0]['message']['content']
            
            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except:
            st.error("Erro na ligação. Verifica a tua API Key nos Secrets.")