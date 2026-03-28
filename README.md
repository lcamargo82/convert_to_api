# Banco LLM - Extrator Universal de Extratos Bancários

Este projeto utiliza inteligência artificial local (Mistral via Ollama) para converter extratos bancários em PDF (de qualquer banco) para Excel/CSV, sem a necessidade de templates complexos.

## Tecnologias
- **Frontend**: Streamlit
- **AI**: Ollama (Mistral)
- **PDF Extraction**: `pdfplumber`

## Como Usar

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

2. Certifique-se de que o [Ollama](https://ollama.com/) está rodando e com o modelo baixado:
   ```bash
   ollama pull mistral
   ollama serve
   ```

3. Execute a aplicação:
   ```bash
   streamlit run app.py
   ```

4. Acesse no navegador (geralmente `http://localhost:8501`), faça upload do seu PDF e aguarde o processamento.

## 🚀 Como Fazer Deploy Gratuito (Streamlit Cloud)

A maneira mais fácil e gratuita de hospedar este projeto é no **Streamlit Community Cloud**.

1.  **Suba este código para o GitHub** (incluindo o arquivo `runtime.txt` que acabei de criar).
2.  Crie uma conta no [share.streamlit.io](https://share.streamlit.io/).
3.  Clique em **"New app"** e selecione este repositório (`lcamargo82/convert-to`).
4.  **Configurações:**
    *   **Main file path:** `app.py`
    *   **Python version:** O Streamlit deve detectar automaticamente o `runtime.txt` (3.11) ou você pode selecionar manualmente 3.11.
5.  **Variáveis de Ambiente (Secrets):**
    *   No painel do Streamlit Cloud, vá em **Settings** > **Secrets**.
    *   Adicione sua chave da Mistral assim:
        ```toml
        MISTRAL_API_KEY = "sua_chave_aqui"
        ```
6.  Clique em **Deploy**! 🚀

### Solução de Problemas
- **Demora no Deploy:** Se estiver demorando muito ("Resolved X packages..."), é porque o Python 3.13 (muito novo) está tentando compilar tudo do zero. O arquivo `runtime.txt` que criei resolve isso forçando o Python 3.11.
- **Erro de chave:** Se der erro de API, verifique se você salvou os "Secrets" corretamente.
