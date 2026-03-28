import sys
import os
import logging
from src.llm_engine import LLMClient
from src.utils import clean_transactions

# Mock data simulating a PDF page content
MOCK_PDF_TEXT = """
Extrato Simplificado
Cliente: Leandro
Conta: 1234-5

Data       Histórico                       Valor
01/01/2024 Saldo Anterior                  1000,00
02/01/2024 PIX RECEBIDO JOAO               150,00
03/01/2024 PGTO BOLETO OTIMO LOJA         -200,50 D
05/01/2024 DEBITO AUTOMATICO NETFLIX       -55,90
07/01/2024 TED ENVIADA MAE                -500,00
08/01/2024 CREDITO SALARIO                4500,00 C
"""

def test_integration():
    print("--- Starting Integration Test ---")
    
    # 1. Check Connection
    client = LLMClient()
    if not client.check_connection():
        print("❌ FAILED: Could not connect to Ollama. Make sure it is running.")
        return

    print("✅ Ollama connection successful.")
    
    # Check if model exists (optional, but good)
    if not client.check_model_availability():
        print(f"⚠️ WARNING: Model '{client.model}' not found in Ollama tags. It might pull it on demand.")
    else:
        print(f"✅ Model '{client.model}' found.")

    # 2. Test Extraction
    print("\n--- Testing Extraction with Mock Text ---")
    print(f"Input Text:\n{MOCK_PDF_TEXT}\n")
    
    try:
        transactions = client.extract_transactions(MOCK_PDF_TEXT)
        print(f"Raw LLM Output (Transactions): {transactions}")
        
        if not transactions:
            print("❌ FAILED: No transactions extracted.")
        else:
            print(f"✅ Extracted {len(transactions)} transactions.")
            
            # 3. Test Cleaning
            print("\n--- Testing Data Cleaning ---")
            df = clean_transactions(transactions)
            print("Resulting DataFrame:")
            print(df)
            
            # Basic validations
            if not df.empty and "Valor" in df.columns:
                print("✅ DataFrame created successfully.")
            else:
                print("❌ FAILED: DataFrame structure incorrect.")

    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_integration()
