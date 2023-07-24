from fastapi.templating import Jinja2Templates
from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import HTMLResponse
from core.models import Message, Chat
from core.schemas import ChatScheme
from db.setup import session


templates = Jinja2Templates(directory="layout/templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def admin_index(request: Request, page: int=Query(1)):

    rows_per_page = 10

    # Calculate the offset for the current page
    offset = (page - 1) * rows_per_page

    # Query the data with pagination
    query = session.query(Chat).limit(rows_per_page).offset(offset)

    # Fetch the results
    users = query.all()

    total_items = query.count()  # Get the total number of items

    # Calculate the total number of pages
    total_pages = (total_items // rows_per_page) + (1 if total_items % rows_per_page > 0 else 0)

    context = {
        "users": users,
        "groups": Chat.groups(),
        "messages": Message.count(),
        "active_users": Chat.active_users(),
        "request": request,
        "chats": Chat.all(),
        "total_pages": total_pages,
        "current_page": page
    }
    
    return templates.TemplateResponse("index.html", context)

