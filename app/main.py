from fastapi import FastAPI

from app.auth.routes import router as auth_router
from app.api.module1_routes import router as module1_router


app = FastAPI(
    title="NOVI API",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(module1_router)