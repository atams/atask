"""
Custom Exception Handlers for atask
Enhanced error messages for better debugging
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
import re

from atams.logging import get_logger

logger = get_logger(__name__)


async def custom_integrity_exception_handler(request: Request, exc: IntegrityError):
    """
    Handle database integrity errors (409) with detailed field information
    Parses the error message to identify which constraint was violated
    """
    error_message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)

    # Initialize default values
    field_name = None
    field_value = None
    constraint_type = "constraint violation"

    # Parse PostgreSQL unique constraint error
    # Example: duplicate key value violates unique constraint "project_prj_code_key"
    # Detail: Key (prj_code)=(qweqwrc) already exists.
    unique_match = re.search(r'Key \(([^)]+)\)=\(([^)]+)\)', error_message)
    if unique_match:
        field_name = unique_match.group(1)
        field_value = unique_match.group(2)
        constraint_type = "unique constraint"
        user_message = f"A record with {field_name} '{field_value}' already exists"

    # Parse foreign key constraint error
    # Example: insert or update on table "task" violates foreign key constraint
    elif "foreign key constraint" in error_message.lower():
        fk_match = re.search(r'Key \(([^)]+)\)=\(([^)]+)\)', error_message)
        if fk_match:
            field_name = fk_match.group(1)
            field_value = fk_match.group(2)
        constraint_type = "foreign key constraint"
        user_message = f"Invalid reference: {field_name} with value '{field_value}' does not exist"

    # Parse NOT NULL constraint error
    elif "null value in column" in error_message.lower():
        null_match = re.search(r'null value in column "([^"]+)"', error_message, re.IGNORECASE)
        if null_match:
            field_name = null_match.group(1)
        constraint_type = "not null constraint"
        user_message = f"Field '{field_name}' is required and cannot be empty"

    # Default fallback message
    else:
        user_message = "Database constraint violation occurred"

    # Log the detailed error for debugging
    logger.warning(
        f"IntegrityError: {constraint_type} - {error_message}",
        extra={
            'extra_data': {
                'path': request.url.path,
                'method': request.method,
                'field': field_name,
                'value': field_value,
                'constraint_type': constraint_type
            }
        }
    )

    # Build response details
    details = {
        "error": user_message,
        "constraint_type": constraint_type
    }

    if field_name:
        details["field"] = field_name

    if field_value:
        details["value"] = field_value

    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "success": False,
            "message": user_message,
            "details": details
        }
    )
