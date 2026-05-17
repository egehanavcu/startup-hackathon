from fastapi import APIRouter, Depends, HTTPException
from app.models import User
from app.schemas import ChatBot
from app.nvidia.chatbot import send_message
from app.routers.auth import get_current_user

router = APIRouter()

@router.post("/chat-bot")
async def post_message(request: ChatBot, current_user: User = Depends(get_current_user)):
    if not current_user.is_teacher:
        raise HTTPException(status_code=403, detail="Bu işlemi yalnızca öğretmenler gerçekleştirebilir")

    response = await send_message(request.message, request.conversation)
    return response
