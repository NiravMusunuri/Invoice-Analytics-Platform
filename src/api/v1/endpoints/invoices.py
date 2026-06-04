from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import date
from uuid import UUID
from fastapi import APIRouter, UploadFile, File
from src.database import get_connection
from src.services.csvparser import save_invoice_csv_to_db


router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"]
)


class InvoiceRequest(BaseModel):
    issuedDate: date
    country: Optional[str] = None
    service: Optional[str] = None
    total: float
    discount: Optional[float] = 0
    tax: Optional[float] = 0
    invoiceStatus: Optional[str] = "pending"
    balance: Optional[float] = None
    dueDate: Optional[date] = None
    client: Optional[Dict[str, Any]] = None


@router.post("/")
def create_invoice(invoice: InvoiceRequest):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chat.invoices (
                    issuedDate,
                    country,
                    service,
                    total,
                    discount,
                    tax,
                    invoiceStatus,
                    balance,
                    dueDate,
                    client
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )
                RETURNING *;
                """,
                (
                    invoice.issuedDate,
                    invoice.country,
                    invoice.service,
                    invoice.total,
                    invoice.discount,
                    invoice.tax,
                    invoice.invoiceStatus,
                    invoice.balance,
                    invoice.dueDate,
                    invoice.client,
                )
            )

            result = cur.fetchone()
            conn.commit()

            return {
                "message": "Invoice created",
                "invoice": result
            }

def upload_invoice_csv(file: UploadFile = File(...)):
    file_bytes = file.file.read()
    return save_invoice_csv_to_db(file_bytes)


@router.get("/")
def get_all_invoices():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM chat.invoices
                ORDER BY issuedDate DESC;
                """
            )

            return cur.fetchall()


@router.get("/{id_invoice}")
def get_invoice(id_invoice: UUID):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM chat.invoices
                WHERE id_invoice = %s;
                """,
                (str(id_invoice),)
            )

            result = cur.fetchone()

            if result is None:
                return {"error": "Invoice not found"}

            return result