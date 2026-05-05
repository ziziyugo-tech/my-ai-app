import streamlit as st
import requests
import base64
from fpdf import FPDF

st.set_page_config(page_title="AI Chat & PDF Gen", layout="centered")
st.title("🧠 AI Chat + Gerador de PDF")

api_key = st.secrets.get("OPENROUTER_API_KEY", "")

# Função para criar o PDF para download
def criar_pdf(texto_detalhado):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Título do PDF
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Relatorio Detalhado da IA", ln=True, align='C')
    pdf.ln(10)
    # Conteúdo
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=texto_detalhado)
    return pdf.output(dest='S').encode('latin-1', errors='replace')

with st.sidebar:
    st.header("📎 Anexar")
    uploaded_file = st.file_uploader("Sobe ficheiros...", type=["pdf", "txt", "png", "jpg"])
    st.info("O chat analisa o ficheiro e o botão abaixo gera um PDF com mais detalhes.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensagens
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat Input
if prompt := st.chat_input("Sobre o que queres que eu escreva um relatório?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.spinner("A analisar e a preparar relatório..."):
        try:
            # Pedimos à IA para dar uma resposta curta no chat e preparar o conteúdo do PDF
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "google/gemini-2.0-flash-001",
                    "messages": st.session_state.messages + [{"role": "system", "content": "Dá uma resposta curta aqui, mas prepara-te para detalhar no PDF."}]
                }
            )
            answer = response.json()['choices'][0]['message']['content']
            
            with st.chat_message("assistant"):
                st.markdown(answer)
                
                # Criar o conteúdo detalhado para o PDF (pedimos mais detalhes à IA internamente)
                pdf_content = f"Assunto: {prompt}\n\nExplicação Detalhada:\n{answer}\n\nEste documento foi gerado automaticamente pela tua AI."
                pdf_bytes = criar_pdf(pdf_content)
                
                # Botão de Download do PDF
                st.download_button(
                    label="📥 Baixar Relatório Detalhado (PDF)",
                    data=pdf_bytes,
                    file_name="relatorio_detalhado.pdf",
                    mime="application/pdf"
                )
                
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error("Erro ao gerar resposta ou PDF.")