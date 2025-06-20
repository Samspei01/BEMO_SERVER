from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router as websocket_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Add the prefix so your route becomes /api/ws/{id}
app.include_router(websocket_router, prefix="/api")