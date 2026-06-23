# Summer-Project
# Summer-Project
# AI Invoice Intelligence Platform

## Overview

This project is an AI-powered invoice intelligence platform built using FastAPI, Streamlit, PostgreSQL, LangGraph, and OpenRouter.

The system allows users to:

* Upload CSV invoice datasets
* Upload PDF invoices
* Extract invoice information using Llama Cloud
* Store invoice data in PostgreSQL
* Query invoice data using natural language
* Generate reports and summaries
* Create graphs and visualizations
* Detect suspicious invoices
* Predict invoice payment status
* Chat with an AI assistant using conversation memory

---

# Architecture

```text
Streamlit UI
      |
      v
FastAPI Backend
      |
      v
LangGraph Agent
      |
      +----------------------+
      |                      |
      v                      v
PostgreSQL              LLM (OpenRouter)
      |
      v
Invoice Data
```

---

# Technologies Used

## Backend

* FastAPI
* Python 3.12
* LangGraph
* LangChain
* OpenRouter

## Frontend

* Streamlit

## Database

* PostgreSQL

## AI / ML

* OpenRouter GPT OSS 120B
* Llama Cloud
* Scikit-learn

## Visualization

* Matplotlib

---

# Features

## Conversational AI

Users can interact with the system using natural language.

Examples:

* How many invoices are overdue?
* Show invoices from India.
* Generate an invoice report.
* Create a graph of invoice statuses.

---

## CSV Upload

Users can upload CSV invoice files.

The system:

1. Reads the CSV
2. Extracts invoice records
3. Stores them in PostgreSQL

---

## PDF Invoice Extraction

Users can upload PDF invoices.

The system:

1. Sends the PDF to Llama Cloud
2. Extracts structured invoice information
3. Stores invoices in PostgreSQL
4. Makes extracted information available for querying

---

## Invoice Reports

Generate business summaries including:

* Total invoices
* Total balances
* Status breakdown
* Country analysis
* Service analysis

---

## Graph Generation

Supported charts:

* Bar charts
* Pie charts
* Line charts

Examples:

* Invoice Status Distribution
* Overdue vs Pending Invoices
* Country Breakdown

---

## Fraud Detection

Identify suspicious invoices based on:

* Missing fields
* Unusual balances
* Abnormal invoice amounts
* Potential anomalies

---

## Invoice Prediction

Predict invoice payment status using a machine learning model.

Inputs:

* Service
* Total
* Discount
* Tax
* Balance

Outputs:

* Predicted Status
* Confidence Scores

---

# Database Schema

## chat.invoices

| Column         | Type        |
| -------------- | ----------- |
| id_invoice     | UUID        |
| invoice_number | TEXT        |
| issuedDate     | DATE        |
| country        | TEXT        |
| service        | TEXT        |
| total          | NUMERIC     |
| discount       | NUMERIC     |
| tax            | NUMERIC     |
| invoiceStatus  | TEXT        |
| balance        | NUMERIC     |
| dueDate        | DATE        |
| client         | JSONB       |
| inserted_ts    | TIMESTAMPTZ |
| updated_ts     | TIMESTAMPTZ |

---

# Agent Tools

## database_query_tool

Converts natural language into SQL queries and retrieves invoice data.

## invoice_report_tool

Generates invoice analytics and summaries.

## invoice_status_graph_tool

Creates invoice status bar charts.

## invoice_status_pie_chart_tool

Creates invoice status pie charts.

## fraud_detection_tool

Detects suspicious invoice activity.

## invoice_prediction_tool

Predicts invoice payment status.

## extract_file_content

Processes uploaded document content.

---

# API Endpoints

## Create Conversation

POST

```text
/conversation
```

Returns a conversation ID.

---

## Chat

POST

```text
/chat
```

Returns an AI response.

---

## Streaming Chat

POST

```text
/chat/stream
```

Streams responses token by token.

---

## Upload CSV

POST

```text
/chat/upload_csv
```

Uploads and stores invoice CSV data.

---

## Upload PDF

POST

```text
/chat/upload_pdf
```

Extracts invoice information from PDF documents.

---

# Installation

Clone the repository:

```bash
git clone <repository_url>
cd project
```

Create virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file:

```env
OPENROUTER_API_KEY="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"
LLAMA_CLOUD_API_KEY="llx-yjXV7HXbydx3R873ADbMH7KkHv9Fn2ZlLu0qTCYZRha1dpf"

DB_HOST=localhost
DB_PORT=5432
DB_NAME=summerproject
DB_USER=postgres
DB_PASSWORD=Musu_nuri09
```

---

# Running FastAPI

```bash
fastapi dev src/main.py
```

---

# Running Streamlit

```bash
streamlit run ui/app.py
```

---

# Future Enhancements

* Image invoice extraction
* Multi-document analysis
* Real-time dashboard
* RAG-based document search
* Advanced fraud detection
* Invoice forecasting
* User authentication
* Export reports to PDF and Excel

```
```

---
# Screenshots



