from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Optional
from starlette import status


class ErrorResponse(BaseModel):
    error_code: str
    message: str
    details: Optional[Any] = None


class AppError(Exception):
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 400,
        details: Any | None = None,
    ) -> None:
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details


class NotFoundError(AppError):
    def __init__(self, entity: str = "Resource"):
        super().__init__(
            error_code="not_found",
            message=f"{entity.capitalize()} not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ForbiddenError(AppError):
    def __init__(self, role: str = "Клиент"):
        super().__init__(
            error_code="forbidden",
            message=f"Доступ запрещен для роли {role}",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ValidationError(AppError):
    def __init__(self, message: str = "Validation error",
                 details: Any | None = None):
        super().__init__(
            error_code="validation_error",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


def init_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error_code=exc.error_code,
                message=exc.message,
                details=exc.details,
            ).model_dump(),
        )