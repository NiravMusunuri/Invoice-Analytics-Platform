from src.database import get_connection
from langchain.agents import create_agent

llm=create_agent(
    model="openrouter:openai/gpt-oss-120b")


def generate_invoice_report():

    with get_connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    COUNT(*) AS total_invoices,
                    SUM(total) AS total_amount,
                    SUM(balance) AS total_balance,
                    AVG(total) AS average_invoice_amount
                FROM chat.invoices;
                """
            )

            summary = cur.fetchone()

            cur.execute(
                """
                SELECT
                    invoiceStatus,
                    COUNT(*) AS invoice_count,
                    SUM(total) AS total_amount,
                    SUM(balance) AS total_balance
                FROM chat.invoices
                GROUP BY invoiceStatus
                ORDER BY invoice_count DESC;
                """
            )

            status_breakdown = cur.fetchall()

            cur.execute(
                """
                SELECT
                    country,
                    SUM(total) AS total_amount
                FROM chat.invoices
                GROUP BY country
                ORDER BY total_amount DESC
                LIMIT 5;
                """
            )

            top_countries = cur.fetchall()

    report_prompt = f"""
Write a professional invoice analytics report.

Overall Metrics:
{summary}

Status Breakdown:
{status_breakdown}

Top Countries:
{top_countries}

Requirements:
- 3-4 paragraphs
- Executive summary
- Total invoices processed
- Total invoice amount
- Outstanding balance analysis
- Paid/Pending/Overdue breakdown
- Top contributing countries
- Notable trends and observations
- Professional business tone
"""

    response = llm.invoke({"messages":[{"role": "user", "content": report_prompt}]})
    return response["messages"][-1].content
