from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from pathlib import Path
import uuid

from src.agent import ask_agent
from src.tools.file_extraction import extract_file_text
from src.services.csvparser import save_invoice_csv_to_db

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

DATA_DIR = Path("src/data")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(file: UploadFile, file_bytes: bytes) -> str:
    file_extension = Path(file.filename).suffix
    safe_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = DATA_DIR / safe_filename

    with open(file_path, "wb") as f:
        f.write(file_bytes)

    return str(file_path)


@router.post("/")
def chat(
    message: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    final_prompt = message
    file_text = ""
    saved_file_path = None
    db_save_result = None

    if file is not None:

        file_bytes = file.file.read()

        saved_file_path = save_uploaded_file(file, file_bytes)

        if file.filename.lower().endswith(".csv"):

            db_save_result = save_invoice_csv_to_db(file_bytes)


        file_text = extract_file_text(file.filename, file_bytes)

    final_prompt = f"""
    User message:
    {message}

    File content:
    {file_text[:10000]}
    """

    response = ask_agent(final_prompt)

    return {
                "user_input": message,
                "saved_file_path": saved_file_path,
                "agent_response": response
            }

