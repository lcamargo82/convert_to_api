import os
import tempfile
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Response
from typing import Optional
from dotenv import load_dotenv

# BLINDAGEM DO .ENV
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, ".env")
load_dotenv(env_path)

chave_salva = os.getenv("MISTRAL_API_KEY")
if chave_salva:
    print(f"✅ DEBUG INICIAL: .env carregado com sucesso! (Chave: {chave_salva[:4]}...{chave_salva[-4:]})")
else:
    print("❌ DEBUG INICIAL: Python não encontrou a MISTRAL_API_KEY no .env!")

# Importando o motor da sua arquitetura
from src.processor import BankStatementProcessor
from src.utils import to_excel_bytes  # <-- Importando a SUA função de gerar Excel!

app = FastAPI(
    title="API Extrator de PDF",
    description="Micro-serviço para extração de extratos bancários com IA",
    version="1.0.0"
)

@app.post("/converter")
async def converter_pdf(
    file: UploadFile = File(...),
    provider: str = Form("mistral"),
    model_name: str = Form("mistral-tiny"),
    api_key: Optional[str] = Form(None), 
    base_url: str = Form("http://localhost:11434")
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="O arquivo deve ser um PDF.")
    
    # BLINDAGEM DO SWAGGER
    if provider == "mistral":
        if not api_key or api_key.strip() == "" or api_key == "string":
            api_key = os.getenv("MISTRAL_API_KEY")
            
        if not api_key:
            raise HTTPException(status_code=401, detail="API Key da Mistral não fornecida e não encontrada no .env.")
            
        api_key = api_key.strip()

    tmp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            conteudo_pdf = await file.read()
            tmp_file.write(conteudo_pdf)
            tmp_path = tmp_file.name

        processor = BankStatementProcessor(
            provider=provider,
            model_name=model_name,
            base_url=base_url,
            api_key=api_key
        )
        
        df = processor.process_pdf(tmp_path)
        
        if df.empty:
            raise HTTPException(status_code=400, detail="Nenhuma transação encontrada no PDF.")

        # --- A MÁGICA DO EXCEL AQUI ---
        # 1. Usa a sua função nativa para transformar o DataFrame em bytes de Excel
        excel_bytes = to_excel_bytes(df)
        
        # 2. Cria o nome do arquivo de saída (ex: Extrato_convertido.xlsx)
        nome_original = file.filename.rsplit('.', 1)[0]
        nome_excel = f"{nome_original}_convertido.xlsx"

        # 3. Devolve para o n8n/Navegador como um arquivo binário baixável
        return Response(
            content=excel_bytes,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={nome_excel}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento da IA: {str(e)}")
    
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
            