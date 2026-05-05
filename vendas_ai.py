import streamlit as st
import requests
import base64
from PIL import Image
from io import BytesIO

# Tenta importar o FPDF, se falhar avisa o utilizador
try:
    from fpdf import FPDF
except ImportError:
    st.error("Instalando componentes... Por favor, aguarde 1 minuto e atualize a página.")

# Tenta importar PyPDF2 para ler ficheiros PDF
try:
    import PyPDF2
except ImportError:
    pass

# 1. Configuração Visual da Página
st.set_page_config(
    page_title="AI Chat & PDF Professional",
    layout="centered",
    page_icon="🤖"
)

# Estilo CSS para uma UI moderna
st.markdown("""
    <style>
    .stDownloadButton > button {
        width: 100%;
        border-radius: 10px;
        background-color: #4B8BBE;
        color: white;
        height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>🤖 AI Chat Professional</h1>", unsafe_allow_html=True)

# Chave API guardada nos Secrets do Streamlit
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

# --- FUNÇÕES DE APOIO ---
def extrair_texto_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    texto = ""
    for page in pdf_reader.pages:
        texto += page.extract_text()
    return texto

def criar_pdf(texto_detalhado):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Relatorio de Analise IA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    # Garante que caracteres especiais não quebram o PDF
    texto_limpo = texto_detalhado.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, txt=texto_limpo)
    return pdf.output(dest='S').encode('latin-1', errors='replace')

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- SIDEBAR (UPLOAD) ---
with st.sidebar:
    st.markdown("<h2 style='color: #4B8BBE;'>📎 Documentos</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Sobe PDF ou Imagem", type=["pdf", "txt", "png", "jpg", "jpeg"])
    
    conteudo_extraido = ""
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            conteudo_extraido = extrair_texto_pdf(uploaded_file)
            st.success("PDF lido!")
        elif uploaded_file.type == "text/plain":
            conteudo_extraido = uploaded_file.read().decode("utf-8")
        st.info("Ficheiro pronto para análise.")

# --- HISTÓRICO DO CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- INPUT DO UTILIZADOR ---
if prompt := st.chat_input("Sobre o que queres falar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("A processar com IA..."):
        try:
            # Prepara a mensagem para a IA (incluindo contexto do ficheiro se houver)
            prompt_final = f"Contexto do ficheiro: {conteudo_extraido}\n\nPergunta: {prompt}"
            conteudo_envio = [{"type": "text", "text": prompt_final}]
            
            # Se for imagem, anexa os dados visuais
            if uploaded_file and uploaded_file.type in ["image/png", "image/jpeg"]:
                base64_img = encode_image(uploaded_file)
                conteudo_envio.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{uploaded_file.type};base64,{base64_img}"}
                })

            # Chamada ao modelo Gemini via OpenRouter
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [{"role": "user", "content": conteudo_envio}]
                }
            )
            
            answer = response.json()['choices'][0]['message']['content']

            with st.chat_message("assistant"):
                st.markdown(answer)
                
                # Botão para descarregar o relatório em PDF
                pdf_bytes = criar_pdf(f"Pergunta: {prompt}\n\nResposta:\n{answer}")
                st.download_button(
                    label="📥 Baixar Relatório Completo (PDF)",
                    data=pdf_bytes,
                    file_name="analise_ia.pdf",
                    mime="application/pdf"
                )

            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"Erro ao ligar à IA: {str(e)}")