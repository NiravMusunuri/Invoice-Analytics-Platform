import pandas as pd


REQUIRED_COLUMNS = [
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


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [
        col.strip()
        for col in df.columns
    ]
    return df


def clean_text_values(df: pd.DataFrame) -> pd.DataFrame:
    text_columns = [
        "country",
        "service",
        "invoiceStatus",
        "client"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.lower()
            )

    return df


def validate_required_columns(df: pd.DataFrame):
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        return {
            "valid": False,
            "error": "Missing required columns",
            "missing_columns": missing_columns
        }

    return {
        "valid": True
    }


def validate_and_clean_invoice_dataframe(df: pd.DataFrame):
    df = clean_column_names(df)
    df = clean_text_values(df)

    validation_result = validate_required_columns(df)

    if not validation_result["valid"]:
        return None, validation_result

    return df, {
        "valid": True,
        "message": "Data cleaned and validated successfully"
    }