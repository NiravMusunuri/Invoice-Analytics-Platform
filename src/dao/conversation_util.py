from src.database import get_connection
import json
from psycopg.types.json import Jsonb



def get_history_from_db(conversation_id: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT message_details_json
                FROM chat.conversations
                WHERE conversation_id = %s;
                """,
                (conversation_id,)
            )

            row = cur.fetchone()

    if row is None:
        return []

    history = row["message_details_json"] or []

    messages = []

    for message in history:
        role = message.get("role")
        content = message.get("content", "")

        if isinstance(content, dict):
            content = content.get("text", "")

        messages.append({
            "role": role,
            "content": content
        })

    return messages








def update_response(response):
    if "structured_response" in response:
        structured_response = response["structured_response"]

        text = structured_response.text
        file_url = structured_response.file_url

        if isinstance(text, str):
            try:
                parsed = json.loads(text)

                if isinstance(parsed, dict):
                    text = parsed.get("text", text)
                    file_url = parsed.get("file_url", file_url)

            except json.JSONDecodeError:
                pass

        return {
            "text": text,
            "file_url": file_url
        }

    final_text = response["messages"][-1].content

    return {
        "text": str(final_text),
        "file_url": None
    }




def save_stream_response(
    conversation_id: str,
    user_message: str,
    assistant_text: str
):
    new_messages = [
        {
            "role": "user",
            "content": user_message
        },
        {
            "role": "assistant",
            "content": {
                "text": assistant_text,
                "file_url": None,
                "streamed": True,
            }
        }
    ]

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE chat.conversations
                SET message_details_json =
                    COALESCE(message_details_json, '[]'::jsonb) || %s
                WHERE conversation_id = %s
                """,
                (
                    Jsonb(new_messages),
                    conversation_id
                )
            )


            conn.commit()
