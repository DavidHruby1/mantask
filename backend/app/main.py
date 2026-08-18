from fastapi import FastAPI, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.endpoints import auth, bootstrap, tasks, teams, users
from backend.app.core.config import settings
from backend.app.error import AppError


api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(bootstrap.router)
api_router.include_router(tasks.router)
api_router.include_router(teams.router)
api_router.include_router(users.router)

app = FastAPI(title=settings.APP_NAME)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health")
def health():
    return {"status": "ok"}
