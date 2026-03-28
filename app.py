import streamlit as st
import pandas as pd
import tempfile
import os
from dotenv import load_dotenv

from src.processor import BankStatementProcessor
from src.llm_engine import LLMClient
from src.utils import to_excel_bytes

# Load environment variables (if any)
load_dotenv()

st.set_page_config(page_title="Extrator Universal - Mistral AI", layout="wide")

st.title("🏦 Extrator de Extratos (Mistral AI)")
st.markdown("""
Este sistema utiliza Inteligência Artificial para ler extratos bancários.
Você pode usar **Ollama (Local/Gratuito)** ou **Mistral API (Nuvem/Rápido)**.
""")

# Sidebar config
st.sidebar.header("⚙️ Configurações da IA")

provider = st.sidebar.radio("Provedor de IA", ["Ollama (Local)", "Mistral API (Nuvem)"])

api_key = None
base_url = "http://localhost:11434"
model_name = "mistral"

if provider == "Ollama (Local)":
    provider_code = "ollama"
    model_name = st.sidebar.text_input("Modelo Ollama", value="mistral")
    base_url = st.sidebar.text_input("URL Ollama", value="http://localhost:11434")
    
    # Check connection
    client = LLMClient(model=model_name, base_url=base_url, provider="ollama")
    if client.check_connection():
        st.sidebar.success(f"🟢 Ollama Conectado")
    else:
        st.sidebar.error("🔴 Ollama off-line")

else: # Mistral API
    provider_code = "mistral"
    model_name = st.sidebar.selectbox("Modelo Mistral", ["mistral-tiny", "mistral-small", "mistral-medium", "mistral-large-latest"], index=0)
    
    # Try getting key from env or input
    env_key = os.getenv("MISTRAL_API_KEY")
    api_key_input = st.sidebar.text_input("Mistral API Key", value=env_key if env_key else "", type="password")
    
    if api_key_input:
        api_key = api_key_input
        client = LLMClient(model=model_name, api_key=api_key, provider="mistral")
        if client.check_connection(): # Takes a bit more time as it inits client
             st.sidebar.success(f"🟢 API Configurada")
    else:
        st.sidebar.warning("⚠️ Insira sua API Key")

# File Uploader
uploaded_file = st.file_uploader("Faça upload do seu extrato (PDF)", type=["pdf"])

if "df_result" not in st.session_state:
    st.session_state.df_result = None

if uploaded_file:
    if st.button("Processar Extrato"):
        if provider_code == "mistral" and not api_key:
             st.error("Para usar a nuvem, você precisa de uma API Key da Mistral.")
             st.stop()
             
        if provider_code == "ollama" and not client.check_connection():
             st.error("Ollama não encontrado. Verifique se está rodando.")
             st.stop()

        with st.spinner(f"Processando com {provider}..."):
            # Save temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            try:
                processor = BankStatementProcessor(
                    provider=provider_code,
                    model_name=model_name,
                    base_url=base_url,
                    api_key=api_key
                )
                
                # Progress bar callback
                progress_bar = st.progress(0)
                def update_progress(current, total):
                    progress_bar.progress(current / total)

                # Process
                df = processor.process_pdf(tmp_path, progress_callback=update_progress)
                
                st.session_state.df_result = df
                st.success("Processamento concluído!")

            except Exception as e:
                st.error(f"Erro durante o processamento: {e}")
            finally:
                os.remove(tmp_path)

# Results Display
if st.session_state.df_result is not None:
    st.divider()
    st.subheader("📝 Verificação e Edição dos Dados")
    st.info("Revise os dados abaixo. Você pode editar valores ou descrições incorretas antes de baixar.")

    # Data Editor
    edited_df = st.data_editor(
        st.session_state.df_result,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Valores": st.column_config.NumberColumn(format="R$ %.2f"),
            "Data": st.column_config.TextColumn(help="Formato esperado: DD/MM ou DD/MM/AAAA"),
            "Tipo": st.column_config.SelectboxColumn(options=["Credit", "Debit"])
        }
    )

    # Export Button
    st.divider()
    col1, col2 = st.columns([1, 4])
    with col1:
        excel_data = to_excel_bytes(edited_df)
        
        # Determine filename
        if uploaded_file:
            original_name = os.path.splitext(uploaded_file.name)[0]
            file_name = f"{original_name}.xlsx"
        else:
            file_name = "extrato_processado.xlsx"

        st.download_button(
            label="📥 Baixar Excel (.xlsx)",
            data=excel_data,
            file_name=file_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )
