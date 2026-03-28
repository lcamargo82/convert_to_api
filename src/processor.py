import logging
import pandas as pd
from typing import List, Dict, Any
from src.extractors import PDFProcessor
from src.llm_engine import LLMClient
from src.utils import clean_transactions

class BankStatementProcessor:
    def __init__(self, provider: str = "ollama", model_name: str = "mistral-tiny", base_url: str = None, api_key: str = None):
        if provider == "ollama":
             # Default fallback if args are None
            base_url = base_url or "http://localhost:11434"
            model_name = model_name or "mistral"
        elif provider == "mistral":
            model_name = model_name or "mistral-tiny"
            
        self.llm_client = LLMClient(model=model_name, base_url=base_url, api_key=api_key, provider=provider)
    
    def process_pdf(self, pdf_path: str, progress_callback=None) -> pd.DataFrame:
        """
        Orchestrates the processing of a single PDF file.
        """
        # 1. Extract Text
        processor = PDFProcessor(pdf_path)
        pages = processor.extract_pages()
        
        if not pages:
            logging.warning(f"No text extracted from {pdf_path}")
            return pd.DataFrame()
        
        all_transactions = []
        total_pages = len(pages)
        
        # 2. Process each page with LLM
        for i, page_text in enumerate(pages):
            if progress_callback:
                progress_callback(i + 1, total_pages)
                
            logging.info(f"Processing page {i+1}/{total_pages}...")
            # We might want to chunk page_text if it's too long, 
            # but usually bank statements fit in context.
            transactions = self.llm_client.extract_transactions(page_text)
            all_transactions.extend(transactions)
            
        # 3. Clean and Structure Data
        df = clean_transactions(all_transactions)
        return df
