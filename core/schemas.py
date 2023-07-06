from pydantic import BaseModel
from datetime import datetime

class ChatScheme(BaseModel):
    id: int
    chat_name: str
    username: str
    is_activated: bool
    chat_id: int
    created_at: datetime
    offset_limit: int
