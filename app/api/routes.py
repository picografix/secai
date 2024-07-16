from fastapi import APIRouter, HTTPException
from schemas.data_request import DataRequest
from schemas.chat_request import ChatRequest
from services.data_services import get_data_api
from services.chat_services import get_chat_response

router = APIRouter()

@router.post("/getData")
async def getData(request: DataRequest):
    try:
        result = await get_data_api(
            request.header, 
            request.year, 
            request.sheetName, 
            request.ticker, 
            force_reload=request.force_reload
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(request: ChatRequest):
    try:
        result = await get_chat_response(
            query= request.query,
            prompt = request.prompt,
            
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))