import pdfplumber
from pathlib import Path
from typing import List, Optional
import logging

class PDFProcessor:
    """
    Handles the extraction of text and basic metadata from PDF files.
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    def extract_text(self) -> str:
        """
        Extracts all text from the PDF, page by page.
        """
        full_text = ""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    # extract_text can return None if no text is found
                    page_text = page.extract_text(x_tolerance=1, y_tolerance=1)
                    if page_text:
                        full_text += page_text + "\n"
        except Exception as e:
            logging.error(f"Error extracting text from {self.pdf_path}: {e}")
            return ""
        
        return full_text

    def extract_pages(self) -> List[str]:
        """
        Returns a list of strings, where each string is the text of a page.
        Useful for processing large documents page-by-page.
        """
        pages_text = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text(x_tolerance=1, y_tolerance=1)
                    if text:
                        pages_text.append(text)
                    else:
                        pages_text.append("") # Keep empty pages to maintain index alignment if needed
        except Exception as e:
            logging.error(f"Error processing pages {self.pdf_path}: {e}")
            return []
        return pages_text
