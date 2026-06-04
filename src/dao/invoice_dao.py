from psycopg.types.json import Jsonb

from src.database import get_connection


def save_invoice_dataframe(df):
    inserted_count = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
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
                    );
                    """,
                    (
                        row["issuedDate"],
                        row["country"],
                        row["service"],
                        row["total"],
                        row["discount"],
                        row["tax"],
                        row["invoiceStatus"],
                        row["balance"],
                        row["dueDate"],
                        Jsonb({"client": row["client"]})
                    )
                )

                inserted_count += 1

            conn.commit()

    return {
        "message": "CSV invoices saved to database",
        "rows_processed": len(df),
        "rows_inserted": inserted_count
    }