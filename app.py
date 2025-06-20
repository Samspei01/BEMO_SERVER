from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router as websocket_router

# Create FastAPI app instance
app = FastAPI()

# Allow cross-origin access for clients or UIs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific domains in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the router with prefix /api
app.include_router(websocket_router)