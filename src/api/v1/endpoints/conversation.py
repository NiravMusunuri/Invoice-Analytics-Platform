from fastapi import APIRouter
from src.services.conversation_services import save_conversation, get_conversation

router = APIRouter(
    prefix="/conversation",
    tags=["Conversation"]
)


@router.post("/")
def create_conversation():
    conversation_id = save_conversation()

    return {
        "message": "Conversation created",
        "conversation_id": conversation_id
    }


@router.get("/{conversation_id}")
def read_conversation(conversation_id: str):
    conversation = get_conversation(conversation_id)

    if conversation is None:
        return {"error": "Conversation not found"}

    return conversation
