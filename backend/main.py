from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.auth import router as auth_router
from backend.routes.folders import router as folders_router
from backend.routes.files import router as files_router
from backend.db.init_db import init_database
app = FastAPI()

app.include_router(auth_router)
app.include_router(folders_router)
app.include_router(files_router)

@app.on_event("startup")
def ensure_database_exists():
    init_database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.get("/")
@app.get("/status")
def ping():
    return {"status": "ok"}