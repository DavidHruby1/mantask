from fastapi import FastAPI

from backend.app.api.endpoints import auth, bootstrap, dashboard

app = FastAPI()

app.include_router(auth.router)
app.include_router(bootstrap.router)
app.include_router(dashboard.router)


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI"}