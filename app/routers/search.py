from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.dependencies import get_db, templates
from app.internal.search import get_results_by_keywords
from app.internal.utils import get_placeholder_user

router = APIRouter()


@router.get("/search")
def search(request: Request) -> Response:
    """Returns the Search page route.

    Args:
        request: The HTTP request.

    Returns:
        The Search HTML page.

    """
    # TODO: connect to current user
    user = get_placeholder_user()

    return templates.TemplateResponse("search.html", {
        "request": request,
        "username": user.username,
    })


@router.post("/search")
async def show_results(request: Request, keywords: str = Form(None),
                       db: Session = Depends(get_db)) -> Response:
    """Returns the Search page route.

    Args:
        request: The HTTP request.
        keywords: The search keywords.
        db: Optional; The database connection.

    Returns:
        The Search HTML page.

    """
    # TODO: connect to current user
    user = get_placeholder_user()

    message = ""
    if not keywords:
        message = _("Invalid request.")
        results = None
    else:
        results = get_results_by_keywords(db, keywords, owner_id=user.id)
        if not results:
            message = _("No matching results for '{keywords}'.")
            message = message.format(keywords=keywords)

    return templates.TemplateResponse("search.html", {
        "request": request,
        "username": user.username,
        "message": message,
        "results": results,
        "keywords": keywords,
    })
