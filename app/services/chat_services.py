import logging
from typing import Any, Dict
from services.llm.chat import Chat

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

chat  = Chat()

async def get_chat_response(query: str, prompt: str) -> Dict[str, Any]:
    """
    Get response from the chat model.
    """
    logger.info(f"Chat API call received for query: {query}, prompt: {prompt}")
    try:
        response = await chat.acall(query, prompt)
        return response
    except Exception as e:
        raise e
 