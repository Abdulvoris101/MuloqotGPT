from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from apps.core.models import Message, Chat
from apps.core.managers import ChatManager, MessageManager
from db.setup import session
from sqlalchemy import desc

templates = Jinja2Templates(directory="layout/templates")

router = APIRouter()

@router.get("/chats", response_class=HTMLResponse)
async def admin_index(request: Request, page: int=Query(1, gt=0)):

    rows_per_page = 15

    # Calculate the offset for the current page
    offset = (page - 1) * rows_per_page
    
    # Query the data without pagination to get the total count
    total_items = ChatManager.count()
    
    # Calculate the total number of pages
    total_pages = (total_items // rows_per_page) + (1 if total_items % rows_per_page > 0 else 0)

    # Query the data with pagination
    query = session.query(Chat).order_by(desc(Chat.id)).limit(rows_per_page).offset(offset)

    chats = query.all()

    all_chats = ChatManager.all()
    
    context = {
        "chats": chats,
        "groups": ChatManager.groups(),
        "messages": Message.count(),
        "active_users": ChatManager.active_users(),
        "all_tokens": MessageManager.all_tokens(),
        "request": request,
        "users": ChatManager.users(),
        "all_chats": all_chats,
        "total_pages": total_pages,
        "current_page": page
    }
    
    return templates.TemplateResponse("index.html", context)



@router.get("/system_messages", response_class=HTMLResponse)
async def system_messages(request: Request):
    all_system_messages = MessageManager.get_system_messages()
    
    context = {
        "groups": ChatManager.groups(),
        "messages": Message.count(),
        "all_tokens": MessageManager.all_tokens(),
        "active_users": ChatManager.active_users(),
        "request": request,
        "users": ChatManager.users(),
        "all_system_messages": all_system_messages
    }
    
    return templates.TemplateResponse("system_messages.html", context)

