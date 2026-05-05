import streamlit as st
import requests
import base64
from fpdf import FPDF
from PIL import Image
from io import BytesIO

# 1. Configuração Visual da Página
st.set_page_config(
    page_title="AI Chat & PDF Generator",
    layout="centered",
    page_icon="🤖"
)

# Estilo CSS para uma UI mais limpa
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stDownloadButton > button {
        width: 100%;
        border-radius: 10px;
        background-color: #4B8BBE;
        color: white;
        height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

# Título Principal
st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>🤖 AI Chat & PDF Professional</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>Analise ficheiros e gere relatórios detalhados instantâneos</p>", unsafe_allow_html=True)

# API Key
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

# Função para criar o PDF (Corrigida para evitar erros de caracteres)
def criar_pdf(texto_detalhado):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Relatorio de Analise IA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=texto_detalhado.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1', errors='replace')

# Função para ler Imagem
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #4B8BBE;'>📎 Documentos</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Sobe ficheiros para análise", type=["pdf", "txt", "png", "jpg"])
    if uploaded_file:
        st.success(f"Ficheiro carregado: {uploaded_file.name}")
    st.info("O chat analisa o ficheiro e gera um PDF detalhado para download.")

# --- CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input do Chat
if prompt := st.chat_input("Sobre o que queres falar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("A processar com IA..."):
        try:
            # Construir conteúdo da mensagem (Texto + Imagem se houver)
            conteudo_envio = [{"type": "text", "text": prompt}]
            
            if uploaded_file and uploaded_file.type in ["image/png", "image/jpeg"]:
                base64_img = encode_image(uploaded_file)
                conteudo_envio.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{uploaded_file.type};base64,{base64_img}"}
                })

            # Chamada à API
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": st.session_state.messages + [{"role": "system", "content": "Dá uma resposta direta. O detalhe irá para o PDF."}]
                }
            )
            
            data = response.json()
            answer = data['choices'][0]['message']['content']

            with st.chat_message("assistant"):
                st.markdown(answer)
                
                # Gerar PDF Detalhado
                pdf_text = f"Analise do pedido: {prompt}\n\nResposta da IA:\n{answer}\n\nFim do Relatorio."
                pdf_bytes = criar_pdf(pdf_text)
                
                st.download_button(
                    label="📥 Baixar Relatório Completo (PDF)",
                    data=pdf_bytes,
                    file_name="relatorio_ai.pdf",
                    mime="application/pdf"
                )

            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"Erro técnico: {str(e)}")