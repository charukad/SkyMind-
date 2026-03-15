from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SkyMind Backend API",
    description="SkyMind AI Airline Operations Intelligence System",
    version="0.1.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "SkyMind Backend"}

from src.api.routes.ml import router as ml_router
from src.api.routes.websockets import router as ws_router

app.include_router(ml_router)
app.include_router(ws_router)

if __name__ == "__main__":
    logger.info("Starting SkyMind Backend Server...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
