# deps.py
from fastapi import Request, HTTPException, status

def get_optional_user_id(request: Request) -> str | None:
    return getattr(request.state, "user_id", None)

def get_required_user_id(request: Request) -> str:
    uid = getattr(request.state, "user_id", None)
    if uid is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Telegram id required")
    return uid

# Fix this one
# # Пример маппинга telegram_id -> internal user (опционально)
# def get_current_user(request: Request, session: Session = Depends(...)):
#     uid = get_required_user_id(request)
#     # Пример: у вас может быть таблица ExternalAccount(provider, provider_id, user_id)
#     # Здесь — упрощённый пример: ищем пользователя по полю telegram_id в users
#     user = repo.read_user(uid, session)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user
