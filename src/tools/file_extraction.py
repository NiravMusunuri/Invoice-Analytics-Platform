from io import BytesIO
import pandas as pd
from pypdf import PdfReader


def extract_file_text(filename: str, file_bytes: bytes) -> str:
    filename = filename.lower()

    if filename.endswith(".txt"):
        return file_bytes.decode("utf-8")

    if filename.endswith(".csv"):
        df = pd.read_csv(BytesIO(file_bytes))
        return df.to_string(index=False)

    if filename.endswith(".pdf"):
        pdf = PdfReader(BytesIO(file_bytes))

        text = ""

        for page in pdf.pages:
            extracted = page.extract_text()

            if extracted:
                text += extracted + "\n"

        return text

    return "Unsupported file type."