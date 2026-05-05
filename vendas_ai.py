import streamlit as st
import requests
import base64
import PyPDF2
from fpdf import FPDF
from PIL import Image
from io import BytesIO

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="AI Chat Professional",
    layout="centered",
    page_icon="🤖"
)

# Estilo CSS para botões e UI
st.markdown("""
    <style>
    .stDownloadButton > button {
        width: 100%;
        border-radius: 10px;
        background-color: #4B8BBE;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# Título
st.markdown("<h1 style='text-align: center; color: #4B8BBE;'>🤖 AI Chat Professional</h1>", unsafe_allow_html=True)

# API Key via Secrets
api_key = st.secrets.get("OPENROUTER_API_KEY", "")

# --- FUNÇÕES DE APOIO ---
def extrair_texto_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        texto = ""
        for page in pdf_reader.pages:
            texto += page.extract_text() or ""
        return texto
    except Exception as e:
        return f"Erro ao ler PDF: {e}"

def criar_pdf(texto_detalhado):
    pdf = FPDF()
    pdf.add_page()
    # Usando Arial (Standard) - Nota: Arial não suporta emojis, por isso limpamos o texto
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Relatorio de Analise IA", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    
    # Limpeza rigorosa para evitar o erro de 'latin-1'
    texto_limpo = texto_detalhado.replace('\u201c', '"').replace('\u201d', '"').replace('\u2013', '-').replace('\u2014', '-')
    texto_final = texto_limpo.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 10, txt=texto_final)
    return pdf.output(dest='S').encode('latin-1')

def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #4B8BBE;'>📎 Documentos</h2>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Sobe PDF ou Imagem", type=["pdf", "txt", "png", "jpg", "jpeg"])
    
    conteudo_extraido = ""
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            conteudo_extraido = extrair_texto_pdf(uploaded_file)
            st.success("PDF processado!")
        elif uploaded_file.type == "text/plain":
            conteudo_extraido = uploaded_file.read().decode("utf-8")
            st.success("Texto lido!")
        else:
            st.info("Imagem carregada para análise visual.")

# --- CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Sobre o que queres falar?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("A aguardar resposta da IA..."):
        try:
            # Contexto do ficheiro + Prompt
            prompt_com_contexto = f"Contexto do ficheiro enviado: {conteudo_extraido}\n\nPergunta do utilizador: {prompt}"
            conteudo_envio = [{"type": "text", "text": prompt_com_contexto}]
            
            # Adicionar imagem se existir
            if uploaded_file and uploaded_file.type in ["image/png", "image/jpeg"]:
                # Reposicionar ponteiro do ficheiro para leitura
                uploaded_file.seek(0)
                img_b64 = encode_image(uploaded_file)
                conteudo_envio.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:{uploaded_file.type};base64,{img_b64}"}
                })

            # Chamada API
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": [{"role": "user", "content": conteudo_envio}]
                }
            )
            
            data = response.json()
            answer = data['choices'][0]['message']['content']

            with st.chat_message("assistant"):
                st.markdown(answer)
                
                # Gerar botão de PDF
                relatorio_texto = f"Pergunta: {prompt}\n\nAnalise:\n{answer}"
                pdf_output = criar_pdf(relatorio_texto)
                
                st.download_button(
                    label="📥 Baixar Resumo em PDF",
                    data=pdf_output,
                    file_name="relatorio_ia.pdf",
                    mime="application/pdf"
                )

            st.session_state.messages.append({"role": "assistant", "content": answer})

        except Exception as e:
            st.error(f"Erro no processamento: {str(e)}")