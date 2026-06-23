from psycopg.types.json import Jsonb
from src.database import get_connection
from src.agent import ask_agent



def chat_with_conversation(
    message: str,
    conversation_id: str
):

    with get_connection() as conn:
        with conn.cursor() as cur:
            response = ask_agent(message, thread_id=conversation_id)
            new_messages = [
                {
                    "role": "user",
                    "content": message
                },
                {
                    "role": "assistant",
                    "content": response
                }
            ]

            cur.execute(
                """
                UPDATE chat.conversations
                SET
                    message_details_json =
                        COALESCE(message_details_json, '[]'::jsonb) || %s,
                    updated_ts = CURRENT_TIMESTAMP
                WHERE conversation_id = %s
                RETURNING message_details_json;
                """,
                (
                    Jsonb(new_messages),
                    conversation_id
                )
            )

            updated = cur.fetchone()

            conn.commit()

            return {
                "conversation_id": conversation_id,
                "user_input": message,
                "agent_response": response,
                "message_details_json": updated["message_details_json"]
            }


