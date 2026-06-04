import pandas as pd
from io import BytesIO

from src.dao.invoice_dao import save_invoice_dataframe


def save_invoice_csv_to_db(file_bytes: bytes):
    df = pd.read_csv(BytesIO(file_bytes))

    required_columns = [
        "issuedDate",
        "country",
        "service",
        "total",
        "discount",
        "tax",
        "invoiceStatus",
        "balance",
        "dueDate",
        "client"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        return {
            "error": "Missing required columns",
            "missing_columns": missing_columns
        }

    return save_invoice_dataframe(df)