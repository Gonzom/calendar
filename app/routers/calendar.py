from fastapi import APIRouter, Request
from fastapi import status
from fastapi.responses import HTMLResponse, Response

from app.dependencies import templates
from app.routers import calendar_grid as cg

router = APIRouter(
    prefix="/calendar/month",
    tags=["calendar"],
    responses={status.HTTP_404_NOT_FOUND: {"description": _("Not found")}},
)

ADD_DAYS_ON_SCROLL: int = 42


@router.get("/")
async def calendar(request: Request) -> Response:
    """Returns the Calendar page route.

    Args:
        request: The HTTP request.

    Returns:
        The Calendar HTML page.
    """
    user_local_time = cg.Day.get_user_local_time()
    day = cg.get_day(user_local_time)
    return templates.TemplateResponse("calendar_monthly_view.html", {
        "request": request,
        "day": day,
        "week_days": cg.Week.DAYS_OF_THE_WEEK,
        "weeks_block": cg.get_month_block(day),
    }
                                      )


@router.get("/{date}")
async def update_calendar(request: Request, date: str) -> HTMLResponse:
    """Returns the Calendar/<date> page route.

    Args:
        request: The HTTP request.
        date: The requested date.

    Returns:
        An updated Calendar HTML page layout.
    """
    last_day = cg.Day.convert_str_to_date(date)
    next_weeks = cg.get_weeks(
        list(cg.get_days_from_date(last_day, ADD_DAYS_ON_SCROLL)))
    template = templates.get_template(
        'partials/calendar/monthly_view/add_week.html')
    content = template.render(weeks_block=next_weeks)
    return HTMLResponse(content=content, status_code=status.HTTP_200_OK)
