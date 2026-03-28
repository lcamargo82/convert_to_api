# 🏦 Banco LLM API - Extrator Universal de Extratos Bancários

Micro-serviço RESTful construído para extrair transações financeiras de extratos bancários em PDF utilizando Inteligência Artificial (Mistral AI via API ou Ollama local). A API lê o documento, estrutura os dados (Data, Descrição, Valor, Tipo) e devolve um arquivo **Excel (.xlsx)** pronto para uso.

Esta API foi desenhada para rodar em background e ser consumida por orquestradores como **n8n**, webhooks ou bots do **Discord**.

## 🛠️ Tecnologias
- **Backend/API:** FastAPI & Uvicorn
- **Inteligência Artificial:** Mistral AI (Nuvem) / Ollama (Local)
- **Extração de PDF:** `pdfplumber`
- **Manipulação de Dados:** `pandas` & `openpyxl`
- **Infraestrutura:** Docker & Docker Compose

---

## 💻 Como Rodar Localmente (Ambiente de Desenvolvimento)

1. Clone o repositório e acesse a pasta do projeto:
   ```bash
   git clone [https://github.com/lcamargo82/convert_to_api.git](https://github.com/lcamargo82/convert_to_api.git)
   cd convert_to_api

2. Crie e ative um ambiente virtual (Recomendado Python 3.11+):
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt

4. Crie um arquivo .env na raiz do projeto e insira sua chave da Mistral (sem aspas):
   ```bash
   MISTRAL_API_KEY=sua_chave_aqui_sem_aspas

5. Inicie o servidor em modo de recarregamento automático:
   ```bash
   uvicorn main:app --reload

6. Teste a API: Abra o navegador e acesse a documentação interativa (Swagger) em http://127.0.0.1:8000/docs. Lá você pode fazer o upload de um PDF e baixar o Excel gerado.


🚀 Como Fazer Deploy em Produção (Docker)
Para rodar em servidores Linux (Ubuntu/Debian) com alta disponibilidade, utilize o Docker.

1. Certifique-se de que o Docker e o Docker Compose estão instalados no servidor.

2. Clone o repositório no servidor e crie o arquivo .env com sua chave da Mistral.

3. Suba o container em background (-d):
   ```bash
   docker compose up -d --build

4. A API estará rodando e blindada na porta 8000 do seu servidor (ex: http://SEU_IP:8000/converter).

Comandos Úteis (Docker)
   - Ver os logs em tempo real: docker logs -f ls-api-conversor

   - Parar a API: docker compose down

   - Reiniciar a API: docker compose restart


📡 Endpoints Principais
POST /converter
   - Recebe um arquivo PDF via multipart/form-data e devolve o arquivo Excel .xlsx correspondente.

   - Parâmetros suportados (Form Data):

   - file (obrigatório): O extrato bancário em formato PDF.

   - provider: mistral (padrão) ou ollama.

   - model_name: Modelo a ser utilizado (ex: mistral-tiny).

   - api_key: (Opcional) Chave da API. Se não for enviada, a API tentará ler do arquivo .env do servidor.