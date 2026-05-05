import streamlit as st
import pandas as pd
import numpy as np
import requests

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="AI Multi-Tool", page_icon="🚀", layout="wide")

# --- CHAVE DE API (Lida dos Secrets do Streamlit) ---
# No Streamlit Cloud, vai a Settings -> Secrets e coloca: OPENROUTER_API_KEY = "tua_chave"
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

# --- BARRA LATERAL (NAVEGAÇÃO) ---
with st.sidebar:
    st.title("🛠️ Ferramentas")
    escolha = st.radio("Ir para:", ["Chat Interativo", "Dashboard & ML", "Upload de Ficheiros"])
    st.divider()
    st.info("Dica: O Chat usa o modelo Qwen-2.5 para te ajudar com código.")

# --- 1. CHATBOX INTERATIVO ---
if escolha == "Chat Interativo":
    st.title("🤖 Chat AI Tutor")
    
    # Memória do chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar mensagens antigas
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada do utilizador
    if prompt := st.chat_input("Pergunta-me qualquer coisa..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Chamada à API
        with st.spinner("A processar..."):
            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": "qwen/qwen-2.5-coder-32b-instruct",
                        "messages": st.session_state.messages
                    }
                )
                res_json = response.json()
                answer = res_json['choices'][0]['message']['content']
                
                with st.chat_message("assistant"):
                    st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except:
                st.error("Erro na API. Verifica se configuraste a chave nos Secrets!")

# --- 2. DASHBOARD & MACHINE LEARNING ---
elif escolha == "Dashboard & ML":
    st.title("📊 Análise de Dados e ML")
    
    # Criar dados de exemplo
    df_demo = pd.DataFrame({
        'Publicidade (k€)': np.random.randint(10, 100, 20),
        'Vendas (u)': np.random.randint(100, 1000, 20)
    })
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tabela de Dados")
        st.dataframe(df_demo, use_container_width=True)
    
    with col2:
        st.subheader("Gráfico de Correlação")
        st.scatter_chart(df_demo, x='Publicidade (k€)', y='Vendas (u)')

    st.divider()
    st.subheader("🤖 Previsão de Machine Learning")
    if st.button("Executar Modelo de Previsão"):
        # Simulação de ML
        st.write("Treinando modelo de Regressão Linear...")
        st.success("Modelo treinado com sucesso! R² Score: 0.85")
        st.metric(label="Previsão Próximo Mês", value="1,450 Unidades", delta="+12%")

# --- 3. UPLOAD DE FICHEIROS ---
elif escolha == "Upload de Ficheiros":
    st.title("📁 Gestão de Ficheiros")
    st.write("Carrega qualquer ficheiro para o servidor.")
    
    uploaded_file = st.file_uploader("Escolher ficheiro", type=["csv", "txt", "pdf", "xlsx"])
    
    if uploaded_file:
        st.success(f"Ficheiro '{uploaded_file.name}' recebido!")
        if ".csv" in uploaded_file.name:
            df_upload = pd.read_csv(uploaded_file)
            st.write("### Conteúdo do CSV:")
            st.table(df_upload.head())