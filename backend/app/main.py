from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.endpoints import auth, bootstrap, tasks
from backend.app.core.config import settings


api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(bootstrap.router)
api_router.include_router(tasks.router)

app = FastAPI(title=settings.APP_NAME)

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
