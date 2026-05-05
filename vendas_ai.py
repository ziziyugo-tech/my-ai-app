import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Configuração da Página
st.set_page_config(page_title="Python Tutor Pro", page_icon="🐍", layout="wide")

st.title("🐍 Python Tutor Pro")
st.markdown("### Interactive Learning Platform")

# Sidebar
with st.sidebar:
    st.header("🔧 Configuração")
    learning_path = st.selectbox("Nível:", ["Iniciante", "Intermédio", "Avançado"])
    data_source = st.radio("Fonte de Dados:", ["Dataset de Exemplo", "Upload CSV"])
    st.divider()
    st.info("Sistema atualizado via Claude 3.5 Sonnet")

# Conteúdo Principal
if data_source == "Dataset de Exemplo":
    np.random.seed(42)
    df = pd.DataFrame({
        'vendas': np.random.randint(100, 1000, 100),
        'publicidade': np.random.randint(50, 500, 100),
        'regiao': np.random.choice(['Norte', 'Sul', 'Este', 'Oeste'], 100)
    })
    
    st.write("### 📊 Visualização de Dados")
    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(df.head(10))
    with col2:
        fig, ax = plt.subplots()
        sns.scatterplot(data=df, x='publicidade', y='vendas', hue='regiao', ax=ax)
        st.pyplot(fig)

    # ML Section
    st.markdown("---")
    st.markdown("### 🤖 Machine Learning")
    X = df[['publicidade']]
    y = df['vendas']
    model = LinearRegression().fit(X, y)
    st.success(f"Modelo treinado com sucesso! R² Score: {model.score(X, y):.2f}")