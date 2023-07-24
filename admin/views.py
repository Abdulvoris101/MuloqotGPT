from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from core.models import Message, Chat
from core.schemas import ChatScheme
from db.setup import session


templates = Jinja2Templates(directory="layout/templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def admin_index(request: Request, page: int=Query(1, gt=0)):

    rows_per_page = 10

    # Calculate the offset for the current page
    offset = (page - 1) * rows_per_page
    
    # Query the data without pagination to get the total count
    total_items = session.query(Chat).count()

    # Calculate the total number of pages
    total_pages = (total_items // rows_per_page) + (1 if total_items % rows_per_page > 0 else 0)

    # Query the data with pagination
    query = session.query(Chat).limit(rows_per_page).offset(offset)
    chats = query.all()

    context = {
        "chats": chats,
        "groups": Chat.groups(),
        "messages": Message.count(),
        "active_users": Chat.active_users(),
        "request": request,
        "users": Chat.users(),
        "total_pages": total_pages,
        "current_page": page
    }
    
    return templates.TemplateResponse("index.html", context)

