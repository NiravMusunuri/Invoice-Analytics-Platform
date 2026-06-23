from src.database import get_connection
from src.tools.graphtool import create_graph


def invoice_status_graph():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT invoiceStatus AS invoicestatus,
                       COUNT(*) AS count
                FROM chat.invoices
                GROUP BY invoiceStatus
                ORDER BY count DESC;
                """
            )

            rows = cur.fetchall()

    x_values = [row["invoicestatus"] for row in rows]
    y_values = [row["count"] for row in rows]

    return create_graph(
        x_values,
        y_values,
        "bar",
        "Invoice Status vs Count"
    )

def invoice_status_pie_chart():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT invoiceStatus AS invoicestatus,
                       COUNT(*) AS count
                FROM chat.invoices
                GROUP BY invoiceStatus
                ORDER BY count DESC;
                """
            )

            rows = cur.fetchall()

    x_values = [row["invoicestatus"] for row in rows]
    y_values = [row["count"] for row in rows]

    return create_graph(
        x_values,
        y_values,
        "pie",
        "Invoice Status Distribution"
    )