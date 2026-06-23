from fastapi import FastAPI
from src.api.v1.endpoints.chat import router as chat_router
from src.api.v1.endpoints.conversation import router as conversation_router
from src.api.v1.endpoints.invoices import router as invoices_router

import logging
from fastapi.staticfiles import StaticFiles

# Configure the logger before creating the app instance
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI()
app.mount(
    "/static",
    StaticFiles(directory="src/data"),
    name="static"
)

app.include_router(invoices_router)
app.include_router(chat_router)
app.include_router(conversation_router)


@app.get("/")
def home():
    return {"message": "FastAPI agent server running"}
