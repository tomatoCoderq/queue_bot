"""Auth module router setup."""

from aiogram import Router

from src.modules.auth.handlers.dialog_handlers import router as dialog_router

# Main router for auth module
router = Router()

# Include dialog handlers
router.include_router(dialog_router)
