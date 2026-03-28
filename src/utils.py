import pandas as pd
from typing import List, Dict, Any
import logging
from io import BytesIO

def clean_transactions(transactions: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Cleans and structures the list of transactions into a DataFrame.
    """
    if not transactions:
        return pd.DataFrame(columns=["Data", "Descrição", "Valor", "Tipo"])

    df = pd.DataFrame(transactions)
    
    # Normalize columns
    col_map = {
        "date": "Data",
        "description": "Descrição",
        "amount": "Valores",
        "type": "Tipo"
    }
    df.rename(columns=lambda x: col_map.get(x.lower(), x), inplace=True)
    
    # Ensure columns exist
    for col in ["Data", "Valores", "Descrição", "Tipo"]:
        if col not in df.columns:
            df[col] = None

    # Clean numeric values
    def clean_money(val):
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            # Try to handle common formats like "1.234,56" vs "1,234.56"
            # This is tricky with LLMs, they usually output standard float format if asked, 
            # but we should be safe.
            val = val.replace("R$", "").strip()
            # If it has comma as decimal separator
            if "," in val and "." in val:
                 # Assume 1.000,00 (PT-BR) -> replace . with nothing, replace , with .
                if val.rfind(',') > val.rfind('.'):
                    val = val.replace('.', '').replace(',', '.')
            elif "," in val:
                val = val.replace(',', '.')
            return float(val)
        return 0.0

    df.loc[:, 'Valores'] = df['Valores'].apply(clean_money)
    
    return df

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    """
    Converts DataFrame to Excel bytes for download, excluding 'Saldo' columns.
    """
    # Filter out columns that contain "saldo" (case insensitive)
    cols_to_keep = [c for c in df.columns if "saldo" not in c.lower()]
    
    # Enforce specific order if columns exist
    desired_order = ["Data", "Valores", "Descrição", "Tipo"]
    final_cols = [c for c in desired_order if c in cols_to_keep] + [c for c in cols_to_keep if c not in desired_order]
    
    df_export = df[final_cols]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='Extrato')
    return output.getvalue()
