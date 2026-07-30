"""Legacy helper: serialize chat history into OpenAI *Responses* API input items.

NOTE: the live tutor (backend/agent.py) talks to Gemini through the standard
``chat.completions`` endpoint and builds its own message list, so this module is
NOT used at runtime. It is kept simple and type-clean so static checks stay green;
it can be deleted safely if you prefer a leaner tree.
"""
from backend.types import Message


def message_items(messages: list[Message]) -> list[dict]:
    """Serialize chat messages into Responses-API-style input items."""
    items: list[dict] = []
    for message in messages:
        content_type = "output_text" if message.role == "assistant" else "input_text"
        items.append(
            {
                "type": "message",
                "role": message.role,
                "content": [{"type": content_type, "text": message.content}],
            }
        )
    return items