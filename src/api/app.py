from src.modules.tasks.routes import router as tasks_router
from src.modules.groups.routes import router as groups_router
from src.modules.users.routes import router as users_router
from src.modules.files.routes import router as files_router
from fastapi import FastAPI
from src.errors import init_exception_handlers
from src.logs import init_logging

app = FastAPI(title="Queue Bot API", version="1.0.0")


init_logging(app)
init_exception_handlers(app)

app.include_router(users_router)
app.include_router(groups_router)
app.include_router(tasks_router)
app.include_router(files_router)

