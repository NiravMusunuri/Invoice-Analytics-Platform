import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from llama_cloud import LlamaCloud

load_dotenv()


INVOICE_SCHEMA = {
    "type": "object",
    "required": ["invoices"],
    "properties": {
        "invoices": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "invoiceNumber",
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
                ],
                "properties": {
                    "invoiceNumber": {"type": "string"},
                    "issuedDate": {"type": "string"},
                    "country": {"type": "string"},
                    "service": {"type": "string"},
                    "total": {"type": "number"},
                    "discount": {"type": "number"},
                    "tax": {"type": "number"},
                    "invoiceStatus": {
                        "type": "string",
                        "enum": ["paid", "pending", "overdue", "unknown"]
                    },
                    "balance": {"type": "number"},
                    "dueDate": {"type": "string"},
                    "client": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                            "phone": {"type": "string"},
                            "address": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
}

def generate_key_insights(extracted_json: dict) -> dict:
    merchant = extracted_json.get("merchant") or {}

    items = extracted_json.get("items") or []

    return {
        "invoice_number": extracted_json.get("invoiceNumber"),
        "receipt_number": extracted_json.get("receiptNumber"),
        "merchant": merchant.get("name"),
        "bill_to": extracted_json.get("billTo"),
        "issued_date": extracted_json.get("issuedDate"),
        "due_date": extracted_json.get("dueDate"),
        "total": extracted_json.get("total"),
        "amount_paid": extracted_json.get("amountPaid"),
        "balance": extracted_json.get("balance"),
        "invoice_status": extracted_json.get("invoiceStatus"),
        "items_count": len(items)
    }


def extract_pdf_with_llama_parse(file_path: str) -> dict:
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")

    if not api_key:
        raise ValueError("LLAMA_CLOUD_API_KEY is not set")

    client = LlamaCloud(api_key=api_key)

    file_obj = client.files.create(
        file=file_path,
        purpose="extract"
    )

    job = client.extract.create(
        file_input=file_obj.id,
        configuration={
            "data_schema": INVOICE_SCHEMA,
            "tier": "cost_effective",
            "extraction_target": "per_doc",
            "parse_tier": "agentic",
            "cite_sources": True,
            "confidence_scores": True
        },
    )

    while job.status not in ("COMPLETED", "FAILED", "CANCELLED"):
        time.sleep(2)
        job = client.extract.get(job.id)

    if job.status != "COMPLETED":
        raise RuntimeError(
            f"Extract job {job.id} ended in {job.status}: {job.error_message}"
        )

    extracted_json = job.extract_result

    output_path = Path(file_path).with_suffix(".extracted.json")
    output_path.write_text(
        json.dumps(extracted_json, indent=2),
        encoding="utf-8"
    )

    extracted_text = json.dumps(
        extracted_json,
        indent=2
    )

    key_insights=generate_key_insights(extracted_json)

    return {
        "extracted_json": extracted_json,
        "extracted_text": extracted_text,
        "json_file_path": str(output_path),
        "key_insights":key_insights
    }