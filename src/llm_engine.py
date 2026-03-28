import requests
import json
import logging
import os
from typing import List, Dict, Any, Optional
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

class LLMClient:
    """
    Client for interacting with LLMs via Ollama (Local) or Mistral API (Cloud).
    """
    def __init__(self, model: str = "mistral-tiny", base_url: str = "http://localhost:11434", api_key: str = None, provider: str = "ollama"):
        self.model = model
        self.provider = provider
        
        # Ollama Config
        self.base_url = base_url
        self.api_generate = f"{base_url}/api/generate"
        self.api_chat = f"{base_url}/api/chat"
        
        # Mistral API Config
        self.api_key = api_key
        self.client = None
        if self.provider == "mistral" and self.api_key:
            try:
                self.client = MistralClient(api_key=self.api_key)
            except Exception as e:
                logging.error(f"Failed to initialize Mistral Client: {e}")

    def check_connection(self) -> bool:
        """Checks connections based on provider."""
        if self.provider == "ollama":
            try:
                response = requests.get(self.base_url)
                return response.status_code == 200
            except requests.exceptions.RequestException:
                return False
        elif self.provider == "mistral":
            return self.client is not None
        return False

    def check_model_availability(self) -> bool:
        """Checks model availability."""
        if self.provider == "ollama":
            try:
                response = requests.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    for m in models:
                        if self.model in m.get('name', ''):
                            return True
                return False
            except Exception:
                return False
        elif self.provider == "mistral":
            # Assume model is available if client is init
            return True 
        return False

    def extract_transactions(self, text_chunk: str) -> List[Dict[str, Any]]:
        """
        Sends a text chunk to the LLM and asks for structured JSON output.
        """
        system_prompt = """
        You are an expert data extraction assistant. Your job is to extract bank transaction details from the provided text.
        
        The text comes from a bank statement PDF.
        Extract the following fields for EACH transaction found:
        - "date": The date of the transaction (keep original format, usually DD/MM or DD/MM/YYYY).
        - "description": The full description of the transaction.
        - "amount": The numeric value. Use negative numbers for debits/withdrawals and positive for credits/deposits.
        - "type": "Credit" or "Debit".

        CRITICAL RULES:
        1. OUTPUT MUST BE PURE JSON. Return a list of objects.
        2. Do not include any markdown formatting. Just the raw JSON string.
        3. If there are no transactions, return an empty list [].
        4. IGNORE "SALDO" COLUMNS: Bank statements often have a running balance column (often labeled "Saldo" or with "C" at the end indicating Credit balance). DO NOT extract these as transactions. Only extract the specific transaction amount.
        5. Ignore header info like "Saldo anterior", "Saldo do dia", or page numbers.
        6. Pay attention to signs (- or D for debits). 
        """

        user_prompt = f"Here is the bank statement text:\n\n{text_chunk}\n\nExtract the transactions as JSON:"

        if self.provider == "mistral":
            return self._extract_via_mistral_api(system_prompt, user_prompt)
        else:
            return self._extract_via_ollama(system_prompt, user_prompt)

    def _extract_via_ollama(self, system_prompt: str, user_prompt: str) -> List[Dict[str, Any]]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "format": "json"
        }

        try:
            response = requests.post(self.api_chat, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            content = result.get('message', {}).get('content', '')
            return self._parse_json_content(content)
        except Exception as e:
            logging.error(f"Error calling Ollama: {e}")
            return []

    def _extract_via_mistral_api(self, system_prompt: str, user_prompt: str) -> List[Dict[str, Any]]:
        if not self.client:
            logging.error("Mistral Client not initialized.")
            return []

        try:
            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=user_prompt)
            ]
            
            # Mistral API usually expects just messages
            # Enforcing JSON format via prompt engineering mostly, 
            # some endpoints support response_format={"type": "json_object"}
            chat_response = self.client.chat(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"}
            )
            
            content = chat_response.choices[0].message.content
            return self._parse_json_content(content)

        except Exception as e:
            logging.error(f"Error calling Mistral API: {e}")
            return []

    def _parse_json_content(self, content: str) -> List[Dict[str, Any]]:
        # Clean up Markdown
        content = content.replace('```json', '').replace('```', '').strip()
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                # Mistral sometimes wraps in a root key
                if "transactions" in data:
                    return data["transactions"]
                # Sometimes it returns just the dict if it's a single object (unlikely here but possible)
                return [data] 
            elif isinstance(data, list):
                return data
            else:
                return []
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON: {content[:100]}...")
            return []
