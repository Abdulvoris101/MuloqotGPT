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
async def admin(request: Request, page: int = Query(1, gt=0)):
    rowsPerPage = 15
    offset = (page - 1) * rowsPerPage
    totalItems = ChatManager.count()
    totalPages = (totalItems // rowsPerPage) + (1 if totalItems % rowsPerPage > 0 else 0)
    query = session.query(Chat).order_by(desc(Chat.id)).limit(rowsPerPage).offset(offset)

    return templates.TemplateResponse("index.html", {
        "chats": query.all(),
        "groups": ChatManager.groupsCount(),
        "messages": Message.count(),
        "activeUsers": ChatActivityManager.getCurrentMonthUsers(),
        "countOfAllInputTokens": ChatActivityManager.countOfAllInputTokens(),
        "countOfAllOutputTokens": ChatActivityManager.countOfAllOutputTokens(),
        "request": request,
        "users": ChatManager.usersCount(),
        "all_chats": ChatManager.all(),
        "total_pages": totalPages,
        "current_page": page
    })


@router.get("/systemMessages", response_class=HTMLResponse)
async def systemMessages(request: Request):
    return templates.TemplateResponse("systemMessages.html", {
        "groups": ChatManager.groupsCount(),
        "messages": Message.count(),
        "countOfAllInputTokens": ChatActivityManager.countOfAllInputTokens(),
        "countOfAllOutputTokens": ChatActivityManager.countOfAllOutputTokens(),
        "activeUsers": ChatActivityManager.getCurrentMonthUsers(),
        "request": request,
        "users": ChatManager.usersCount(),
        "all_systemMessages": MessageManager.getSystemMessages()
    })

