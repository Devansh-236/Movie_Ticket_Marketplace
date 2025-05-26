from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from routers import tickets, movies, events
from services.dynamodb_service import DynamoDBService

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Movie Booking FastAPI...")
    
    # Initialize DynamoDB service
    dynamodb_service = DynamoDBService()
    app.state.dynamodb_service = dynamodb_service
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Movie Booking FastAPI...")

app = FastAPI(
    title="Movie Booking API",
    description="A FastAPI-based movie ticket booking system with LocalStack integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tickets.router, prefix="/api", tags=["tickets"])
app.include_router(movies.router, prefix="/api", tags=["movies"])
app.include_router(events.router, prefix="/api", tags=["events"])

@app.get("/")
async def root():
    return {
        "message": "Movie Booking API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "movie-booking-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
