from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str
    max_tokens: int = 50
    temperature: float = 0.7
    top_p: float = 0.95
    query: str