from psycopg.types.json import Jsonb
from src.database import get_connection


def is_valid_invoice(invoice: dict) -> bool:
    if not invoice.get("invoiceNumber"):
        return False

    if not invoice.get("issuedDate"):
        return False

    if not invoice.get("dueDate"):
        return False

    if not invoice.get("total"):
        return False

    return True


def save_pdf_invoices_to_db(invoices: list[dict]):
    inserted_ids = []
    skipped = []

    with get_connection() as conn:
        with conn.cursor() as cur:
            for invoice in invoices:
                if not is_valid_invoice(invoice):
                    skipped.append(invoice)
                    continue

                cur.execute(
                    """
                    INSERT INTO chat.invoices (
                        invoice_number,
                        issueddate,
                        country,
                        service,
                        total,
                        discount,
                        tax,
                        invoicestatus,
                        balance,
                        duedate,
                        client
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id_invoice;
                    """,
                    (
                        invoice.get("invoiceNumber"),
                        invoice.get("issuedDate"),
                        invoice.get("country") or "unknown",
                        invoice.get("service") or "unknown",
                        invoice.get("total") or 0,
                        invoice.get("discount") or 0,
                        invoice.get("tax") or 0,
                        invoice.get("invoiceStatus") or "pending",
                        invoice.get("balance") or 0,
                        invoice.get("dueDate"),
                        Jsonb(invoice.get("client") or {})
                    )
                )

                row = cur.fetchone()
                inserted_ids.append(str(row["id_invoice"]))

            conn.commit()

    return {
        "inserted_ids": inserted_ids,
        "inserted_count": len(inserted_ids),
        "skipped_count": len(skipped),
        "skipped_invoices": skipped
    }