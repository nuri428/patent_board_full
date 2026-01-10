from fastapi import APIRouter

router = APIRouter()


@router.post("/ask")
async def ask_question():
    return {"message": "Chat endpoint"}


@router.get("/history")
async def get_chat_history():
    return {"message": "Chat history endpoint"}