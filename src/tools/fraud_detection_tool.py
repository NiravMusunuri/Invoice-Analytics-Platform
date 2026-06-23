from src.database import get_connection


def detect_suspicious_invoices(limit: int = 20):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    id_invoice,
                    country,
                    service,
                    total,
                    discount,
                    tax,
                    balance,
                    invoiceStatus,
                    ROUND((discount / NULLIF(total, 0)) * 100, 2) AS discount_percent,
                    ROUND((tax / NULLIF(total, 0)) * 100, 2) AS tax_percent,
                    ROUND((balance / NULLIF(total, 0)) * 100, 2) AS balance_percent
                FROM chat.invoices
                WHERE
                    total > 0
                    AND (
                        (discount / NULLIF(total, 0)) > 0.40
                        OR (tax / NULLIF(total, 0)) > 0.30
                        OR (balance / NULLIF(total, 0)) > 0.90
                        OR total > (
                            SELECT AVG(total) + 2 * STDDEV(total)
                            FROM chat.invoices
                        )
                    )
                ORDER BY total DESC
                LIMIT %s;
                """,
                (limit,)
            )

            rows = cur.fetchall()

    return {
        "suspicious_invoice_count": len(rows),
        "suspicious_invoices": rows
    }