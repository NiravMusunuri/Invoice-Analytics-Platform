import os

from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openai import ChatOpenAI

from src.tools.prompt import run_query_agent
from src.tools.invoicesreport import generate_invoice_report


def extract_file_content(file_text: str) -> str:
    """
    Extract and analyze uploaded file content.

    Use this tool when the user uploads a file
    and asks questions about it.
    """
    return f"Extracted file content:\n\n{file_text}"


def database_query_tool(question: str):
    """
    Convert natural language into SQL,
    query PostgreSQL,
    and summarize the result.
    """
    return run_query_agent(question)


def invoice_report_tool():
    """
    Generate a narrative invoice report from database metrics.
    """
    return generate_invoice_report()


memory = InMemorySaver()


agent = create_agent(
    model="openrouter:openai/gpt-oss-120b",

    tools=[
        extract_file_content,
        database_query_tool,
        invoice_report_tool
    ],

system_prompt="""
You are a helpful AI assistant.

If the user greets you casually, respond naturally and briefly.

Use tools only when needed.

Available capabilities:
- File extraction
- Database invoice querying
- Invoice report generation

When users ask about invoices, balances, countries, totals,
statuses, or conversations, use the database_query_tool.

When users ask for an invoice report, invoice summary,
financial overview, or business report, use invoice_report_tool.

When users upload files and ask questions about them,
use extract_file_content.
""",

    checkpointer=memory,
)


def ask_agent(
    user_message: str,
    thread_id: str = "1",
    history=None
):

        messages = []

        if history:
            messages.extend(history)

        messages.append({
            "role": "user",
            "content": user_message
        })

        response = agent.invoke(
            {
                "messages": messages
            },
            {
                "configurable": {
                    "thread_id": thread_id
                }
            },
        )

        return response["messages"][-1].content

