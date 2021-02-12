import datetime

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.dependencies import templates

router = APIRouter()


# TODO: Add this as a feature to the calendar view /
#  day view / features panel frontend


@router.get("/currency")
def today_currency(request: Request) -> Response:
    """Returns the Currency route with data for today.

    Args:
        request: The HTTP request.

    Returns:
        The current day Currency HTML page.

    """
    date = datetime.date.today().strftime("%Y-%m-%d")
    return currency(request, date)


@router.get("/currency/{date}")
def currency(request: Request, date: str) -> Response:
    """Returns the Currency route with specific date data.

    Args:
        request: The HTTP request.
        date: The date for the requested information.

    Returns:
        The current day Currency HTML page.

    """
    # TODO: get user default/preferred currency
    currency_type = "USD"

    return templates.TemplateResponse("currency.html", {
        "request": request,
        "currency": currency_type,
        "date": date,
    })
