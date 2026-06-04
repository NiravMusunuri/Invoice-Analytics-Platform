from src.database import get_connection


def save_conversation():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chat.conversations DEFAULT VALUES
                RETURNING conversation_id;
                """
            )

            result = cur.fetchone()
            conn.commit()

            return result["conversation_id"]


def get_conversation(conversation_id: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM chat.conversations
                WHERE conversation_id = %s;
                """,
                (conversation_id,)
            )

            return cur.fetchone()