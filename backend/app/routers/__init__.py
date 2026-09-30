from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.resumes import router as resumes_router
from app.routers.jobs import router as jobs_router
from app.routers.analyze import router as analyze_router
from app.routers.history import router as history_router
from app.routers.dashboard import router as dashboard_router
from app.routers.chat import router as chat_router

__all__ = [
    "auth_router",
    "users_router",
    "resumes_router",
    "jobs_router",
    "analyze_router",
    "history_router",
    "dashboard_router",
    "chat_router"
]
