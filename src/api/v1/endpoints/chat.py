from venv import logger

from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional
from pathlib import Path
import uuid

from src.agent import ask_agent
from src.tools.file_extraction import extract_file_text
from src.services.csvparser import save_invoice_csv_to_db
from src.pdf_parser import extract_pdf_with_llama_parse
from src.pdf_parser import extract_pdf_with_llama_parse
from src.dao.pdf_dao import save_pdf_invoices_to_db

from fastapi.responses import StreamingResponse
from src.agent import ask_agent,stream_agent

import logging

logger = logging.getLogger(__name__)

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
    conversation_id: Optional[str] = Form(None),
    document_text: Optional[str] = Form("")
):
    final_prompt = message

    if document_text:
        final_prompt = f"""
You are answering questions about an uploaded PDF.

PDF CONTENT:
{document_text[:15000]}

USER QUESTION:
{message}

Answer ONLY using the PDF if possible.
If the answer is not present in the PDF, clearly state that.
"""

    response = ask_agent(
        user_message=final_prompt,
        thread_id=conversation_id
    )

    return {
        "user_input": message,
        "agent_response": response
    }


@router.post("/upload_csv")
def upload_csv(file: UploadFile = File(...)):
    file_bytes = file.file.read()
    saved_file_path = save_uploaded_file(file, file_bytes)
    db_save_result = save_invoice_csv_to_db(file_bytes)

    return {
        "message": "CSV uploaded and saved to database",
        "saved_file_path": saved_file_path,
        "rows_processed": db_save_result["rows_processed"],
        "rows_inserted": db_save_result["rows_inserted"]
    }

@router.post("/upload_pdf")
def upload_pdf(file: UploadFile = File(...)):
    file_bytes = file.file.read()
    saved_file_path = save_uploaded_file(file, file_bytes)

    parse_result = extract_pdf_with_llama_parse(saved_file_path)

    invoices = parse_result["extracted_json"].get("invoices", [])

    inserted_ids = save_pdf_invoices_to_db(invoices)

    return {
        "message": "PDF invoices parsed and saved to invoices table",
        "rows_inserted": len(inserted_ids),
        "inserted_invoice_ids": inserted_ids,
        "saved_file_path": saved_file_path,
        "extracted_text": parse_result["extracted_text"][:15000],
        "key_insights": {
            "invoice_count": len(invoices),
            "inserted_count": len(inserted_ids)
        }
    }

@router.post("/upload_image")
def upload_image(file: UploadFile = File(...)):
    file_bytes = file.file.read()
    saved_file_path = save_uploaded_file(file, file_bytes)

    parse_result = extract_pdf_with_llama_parse(saved_file_path)

    invoices = parse_result["extracted_json"].get("invoices", [])

    inserted_ids = save_pdf_invoices_to_db(invoices)

    save_result = save_pdf_invoices_to_db(invoices)

    return {
        "message": "PDF invoices parsed and saved to invoices table",
        "rows_inserted": save_result["inserted_count"],
        "rows_skipped": save_result["skipped_count"],
        "inserted_invoice_ids": save_result["inserted_ids"],
        "saved_file_path": saved_file_path,
        "extracted_text": parse_result["extracted_text"][:15000],
        "key_insights": {
            "invoice_count": len(invoices),
            "inserted_count": save_result["inserted_count"],
            "skipped_count": save_result["skipped_count"]
        }
    }

@router.post("/stream")
def chat_stream(
    message: str = Form(...),
    conversation_id: Optional[str] = Form(None),
    document_text: Optional[str] = Form("")
):
    logger.info(f"starting chat stream :: {conversation_id}")
    final_prompt = message

    if document_text:
        final_prompt = f"""
You are answering questions about an uploaded document.

Document:
{document_text[:15000]}

User question:
{message}
"""

    return StreamingResponse(
        stream_agent(
            user_message=final_prompt,
            thread_id=conversation_id
        ),
        media_type="text/plain"
    )



