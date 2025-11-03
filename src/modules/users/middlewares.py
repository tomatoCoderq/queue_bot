# auth_middleware.py
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
import logging

class TelegramIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        tg_header = request.headers.get("X-Telegram-Id")
        user_id: Optional[str] = None

        if tg_header:
            user_id = tg_header.strip()
        else: 
            raise HTTPException(status_code=401, detail="X-Telegram-Id header missing")

        request.state.user_id = user_id

        response = await call_next(request)
        return response
