import re
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import status
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.datastructures import ImmutableMultiDict

from app.database.models import Category
from app.dependencies import get_db
from app.internal.utils import get_placeholder_user

HEX_COLOR_FORMAT = r"^(?:[0-9a-fA-F]{3}){1,2}$"

router = APIRouter(
    prefix="/categories",
    tags=["categories"],
)


# TODO: Should this be here or in /database/models?
class CategoryModel(BaseModel):
    name: str
    color: str
    user_id: int

    class Config:
        schema_extra = {
            "example": {
                "name": "Guitar lessons",
                "color": "aabbcc",
                "user_id": get_placeholder_user().id,
            }
        }


# TODO(issue#29): get current user_id from session
@router.get("/")
def get_categories(request: Request,
                   db: Session = Depends(get_db)) -> List[Category]:
    """Returns a list of categories for a requested user.

    Args:
        request: The HTTP request.
        db: Optional; The database connection.

    Returns:
        A list of categories for a requested user.

    Raises:
        HTTPException: If the request.query_params are not valid.

    """
    if _is_query_params_valid(request.query_params):
        return _get_user_categories(db, **request.query_params)
    else:
        message = _("Request {request} contains illegal parameters.")
        message = message.format(request=request)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


# TODO(issue#29): get current user_id from session
@router.post("/")
async def set_category(category: CategoryModel,
                       db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Saves a category to the user's table in the database.

    If the save is successful, returns the saved object as a dictionary.
    If the save fails, raises an exception.

    Args:
        category: The category to add to the user.
        db: Optional; The database connection.

    Returns:
        A dict with the category_entry attributes.

    Raises:
        HTTPException: If the category already exists for the user,
        or if the color is not in a valid format.

    """
    if not _is_color_format_valid(category.color):
        message = _("Color {color} is not in a valid format.")
        message = message.format(color=category.color)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
    try:
        category_entry = Category.create(
            db,
            name=category.name,
            color=category.color,
            user_id=category.user_id,
        )
    except IntegrityError:
        db.rollback()
        message = _("The category already exists for user {id}.")
        message = message.format(id=category.user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )
    else:
        return {"category": category_entry.to_dict()}


def _is_query_params_valid(query_params: ImmutableMultiDict) -> bool:
    """Checks if the request.query_params is valid or not.

    The request.query_params must contain user_id and can contain
    also the fields name and color.
    Intersection must contain at least user_id.
    Union must not contain fields other than user_id, name, color.
    color must be valid.

    Args:
        query_params: The request.query_params

    Returns:
        True if the query_params pass the described validation,
        False otherwise.

    """
    is_valid_color = True
    all_fields = set(CategoryModel.schema()["required"])
    request_params = set(query_params)
    union_set = request_params.union(all_fields)
    intersection_set = request_params.intersection(all_fields)

    if "color" in intersection_set:
        is_valid_color = _is_color_format_valid(query_params["color"])

    return (union_set == all_fields
            and "user_id" in intersection_set
            and is_valid_color
            )


def _is_color_format_valid(color: str) -> bool:
    """Checks if the color is from a valid hex format (without `#`).

    Args:
        color: A hex color.

    Returns:
        True if the color is valid, False otherwise.

    """
    if color:
        return re.fullmatch(HEX_COLOR_FORMAT, color) is not None
    return False


def _get_user_categories(db: Session,
                         user_id: int, **params) -> List[Category]:
    """Returns the user's categories, filtered by parameters.

    Args:
        db: The database connection.
        user_id: The user's ID.
        **params: TODO: add description

    Returns:
        A list of the user's Categories.

    """
    try:
        categories = (
            db.query(Category)
            .filter_by(user_id=user_id)
            .filter_by(**params)
            .all()
        )
    except SQLAlchemyError:
        return []
    else:
        return categories
