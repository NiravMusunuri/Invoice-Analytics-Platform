import os
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain_openrouter import ChatOpenRouter
from dotenv import load_dotenv

load_dotenv()


from src.tools.prompt import run_query_agent
from src.tools.invoicesreport import generate_invoice_report
from src.tools.graphtool import create_graph
from src.tools.invoicegraphtool import invoice_status_graph, invoice_status_pie_chart
from src.tools.fraud_detection_tool import detect_suspicious_invoices
from pydantic import BaseModel, Field
from typing import Optional

from langchain.agents.structured_output import ToolStrategy
from src.dao.conversation_util import get_history_from_db, update_response, save_stream_response
from src.ML.predict_invoice_status import predict_invoice_status
from langchain_core.messages import AIMessageChunk


class ResponseFormat(BaseModel):
    text: str = Field(description="Final agent response")
    file_url: Optional[str] = Field(default=None, description="Optional complete file URL if a file/graph was created")


def extract_file_content(file_text: str):
    """
    Analyze uploaded document content.

    Use this tool when:
    - a file was uploaded
    - the user asks questions about the uploaded file
    - the user asks to summarize the uploaded file
    - the user asks to extract information from a document

    Do not use for database questions.
    """
    return f"Extracted file content:\n\n{file_text}"


def database_query_tool(question: str):
    """
    Query the invoice database using natural language.

    Use this tool when users ask about:
    - invoice counts
    - invoice totals
    - balances
    - countries
    - services
    - payment status
    - overdue invoices
    - database records

    Do not use for general conversation.
    """
    return run_query_agent(question)


def invoice_report_tool():
    """
    Generate a business summary of invoice data.

    Use this tool when users ask for:
    - invoice reports
    - financial summaries
    - invoice analytics
    - business insights
    - management reports
    """
    return generate_invoice_report()

def graph_creation_tool(x_values: list, y_values: list, graph_type: str = "bar", title: str = "Generated Graph"):
    """
    Create a graph from x and y values.

    Use this tool when the user asks to draw, plot, create, or generate a graph/chart,
    Currently supports:
    - bar chart
    """
    return create_graph(
        x_values=x_values,
        y_values=y_values,
        graph_type=graph_type,
        title=title
    )

def invoice_status_graph_tool():
    """
    Create a bar chart showing invoice status distribution.

    Use this tool when users ask for:
    - invoice status graph
    - invoice bar chart
    - paid vs pending vs overdue chart
    - visualize invoice statuses
    """
    return invoice_status_graph()


def invoice_status_pie_chart_tool():
    """
    Create a pie chart of invoice statuses.

    Use this tool when users ask for:
    - invoice status pie chart
    - invoice distribution
    - percentage of paid invoices
    - status breakdown
    """
    return invoice_status_pie_chart()
def invoice_prediction_tool(
    service: str,
    total: float,
    discount: float,
    tax: float,
    balance: float
):
    """
    Predict invoice payment status.

    Requires:
    - service
    - total
    - discount
    - tax
    - balance
    """

    return predict_invoice_status(
        service=service,
        total=total,
        discount=discount,
        tax=tax,
        balance=balance
    )


def fraud_detection_tool(limit: int = 20):
    """
    Detect suspicious invoices.

    Use this tool when users ask for:
    - fraud detection
    - suspicious invoices
    - anomalies
    - invoice audit
    - unusual transactions
    - risky invoices
    """
    return detect_suspicious_invoices()



memory = InMemorySaver()

llm = ChatOpenRouter(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

SYSTEM_PROMPT = """
You are a helpful AI assistant.

If the user greets you casually, respond naturally and briefly.

Use tools only when needed.

Available capabilities:
- File extraction
- Database invoice querying
- Invoice report generation
- Graph generation
- Fraud detection
- Invoice prediction

When users ask about invoices, balances, countries, totals,
statuses, or conversations, use the database_query_tool.

When users ask for an invoice report, invoice summary,
financial overview, or business report, use invoice_report_tool.

When users upload files and ask questions about them,
use extract_file_content.

When the user asks to draw a graph from invoice data:
1. First use database_query_tool to get the needed data.
2. Then use graph_creation_tool using the returned categories as x_values and counts/amounts as y_values.
3. Return the generated graph path.

When the user specifically asks for:
- invoice status bar chart -> invoice_status_graph_tool
- invoice status pie chart -> invoice_status_pie_chart_tool
- fraud detection -> fraud_detection_tool
- invoice prediction -> invoice_prediction_tool

Do not truncate graph paths or file URLs.
"""

agent = create_agent(
    model=llm,
    tools=[
        extract_file_content,
        database_query_tool,
        invoice_report_tool,
        graph_creation_tool,
        invoice_status_graph_tool,
        invoice_status_pie_chart_tool,
        invoice_prediction_tool,
        fraud_detection_tool
    ],
    response_format=ToolStrategy(ResponseFormat),
    system_prompt=SYSTEM_PROMPT,
    checkpointer=memory,
)

streaming_llm_agent = create_agent(
    model=llm,
    tools=[
        extract_file_content,
        database_query_tool,
        invoice_report_tool,
        graph_creation_tool,
        invoice_status_graph_tool,
        invoice_status_pie_chart_tool,
        invoice_prediction_tool,
        fraud_detection_tool
    ],
    response_format=ToolStrategy(ResponseFormat),
    system_prompt=SYSTEM_PROMPT + """

Answer in plain English.

Do NOT return JSON.
Do NOT wrap responses in:
{"text":"..."}

Do NOT show SQL queries unless the user explicitly asks for SQL.

Only provide the final answer.
""",
    checkpointer=memory,
)


def ask_agent(
    user_message: str,
    thread_id: str = None
):
    messages = []

    if thread_id:
        messages = get_history_from_db(thread_id)

    messages.append({
        "role": "user",
        "content": user_message
    })

    response = agent.invoke(
        {"messages": messages},
        {
            "configurable": {
                "thread_id": thread_id or "no-conversation"
            }
        }
    )

    print("@@@", response)

    return update_response(response)







def stream_agent(
    user_message: str,
    thread_id: str | None = None
):
    messages = []

    if thread_id:
        messages = get_history_from_db(thread_id)

    messages.append({
        "role": "user",
        "content": user_message
    })

    config = {
        "configurable": {
            "thread_id": thread_id or "no-conversation"
        }
    }

    full_response = ""

    for chunk in streaming_llm_agent.stream(
        {"messages": messages},
        config=config,
        stream_mode="messages"
    ):
        token, metadata = chunk

        if metadata.get("langgraph_node") != "model":
            continue

        if isinstance(token, AIMessageChunk):
            if token.content:
                full_response += token.content
                yield token.content

    if thread_id and full_response:
        print("##", full_response)
        save_stream_response(
            conversation_id=thread_id,
            user_message=user_message,
            assistant_text=full_response
        )






