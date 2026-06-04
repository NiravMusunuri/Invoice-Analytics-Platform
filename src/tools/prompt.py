from src.database import get_connection
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite"
)

SCHEMA_CONTEXT = """
You have access to a PostgreSQL database with these tables:

chat.invoices (
    id_invoice,
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

chat.conversations (
    conversation_id,
    title,
    message_details_json,
    summary,
    feedback_json,
    user_details_json,
    inserted_ts,
    updated_ts
)

When the user asks a question, generate a single valid PostgreSQL SELECT query.

Return ONLY the SQL query.
No explanation.
No markdown.
Only use SELECT.

Never use:
INSERT
UPDATE
DELETE
DROP
ALTER
TRUNCATE
"""


def clean_sql(sql: str) -> str:
    return sql.replace("```sql", "").replace("```", "").strip()


def is_safe_sql(sql: str) -> bool:
    sql_lower = sql.lower()

    blocked_words = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "truncate",
        "create"
    ]

    if not sql_lower.startswith("select"):
        return False

    for word in blocked_words:
        if word in sql_lower:
            return False

    return True


def run_query_agent(question: str):

    sql_response = llm.invoke(
        f"""
{SCHEMA_CONTEXT}

Question:
{question}

SQL:
"""
    )

    sql = clean_sql(sql_response.content)

    if not is_safe_sql(sql):
        return {
            "error": "Unsafe SQL blocked",
            "sql": sql
        }

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(sql)

                rows = cur.fetchall()

    except Exception as e:
        return {
            "error": str(e),
            "sql": sql
        }

    summary_response = llm.invoke(
        f"""
The user asked:
{question}

The SQL query was:
{sql}

The results are:
{rows[:20]}

Write a short answer in 2-3 sentences.
"""
    )

    return {
        "question": question,
        "sql": sql,
        "rows": rows,
        "row_count": len(rows),
        "answer": summary_response.content
    }