from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from core.models import Message, Chat

templates = Jinja2Templates(directory="layout/templates")

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def admin_index(request: Request):
    context = {
        "users": Chat.users(),
        "groups": Chat.groups(),
        "messages": Message.count(),
        "active_users": Chat.active_users(),
        "request": request,
        "chats": Chat.all()
    }
    return templates.TemplateResponse("index.html", context)