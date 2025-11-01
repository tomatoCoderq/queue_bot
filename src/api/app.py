from src.modules.tasks.routes import router as tasks_router
from src.modules.groups.routes import router as groups_router
from src.modules.users.routes import router as users_router
from fastapi import FastAPI

app = FastAPI(title="Queue Bot API", version="1.0.0")


app.include_router(users_router)
app.include_router(groups_router)
app.include_router(tasks_router)
