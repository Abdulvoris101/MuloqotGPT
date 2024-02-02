from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from apps.core.models import Message, Chat
from apps.core.managers import ChatManager, MessageManager, ChatActivityManager
from db.setup import session
from sqlalchemy import desc

templates = Jinja2Templates(directory="layout/templates")

router = APIRouter()

@router.get("/chats", response_class=HTMLResponse)
async def adminIndex(request: Request, page: int=Query(1, gt=0)):

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
        "groups": ChatManager.groupsCount(),
        "messages": Message.count(),
        "activeUsers": ChatManager.activeUsers(),
        "countOfAllInputTokens": ChatActivityManager.countOfAllInputTokens(),
        "countOfAllOutputTokens": ChatActivityManager.countOfAllOutputTokens(),
        "request": request,
        "users": ChatManager.usersCount(),
        "all_chats": all_chats,
        "total_pages": total_pages,
        "current_page": page
    }
    
    return templates.TemplateResponse("index.html", context)



@router.get("/systemMessages", response_class=HTMLResponse)
async def systemMessages(request: Request):
    all_systemMessages = MessageManager.getSystemMessages()
    
    context = {
        "groups": ChatManager.groupsCount(),
        "messages": Message.count(),
        "countOfAllInputTokens": ChatActivityManager.countOfAllInputTokens(),
        "countOfAllOutputTokens": ChatActivityManager.countOfAllOutputTokens(),
        "activeUsers": ChatManager.activeUsers(),
        "request": request,
        "users": ChatManager.usersCount(),
        "all_systemMessages": all_systemMessages
    }
    
    return templates.TemplateResponse("systemMessages.html", context)

