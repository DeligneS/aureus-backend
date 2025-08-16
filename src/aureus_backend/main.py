from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from aureus_backend.api.v1.auth.google import router as google_auth_router
from aureus_backend.api.v1.auth.credentials import router as credentials_router
from aureus_backend.api.v1.banking.banks import router as banking_banks_router
from aureus_backend.api.v1.banking.connect import router as banking_connect_router
from aureus_backend.api.v1.banking.accounts import router as banking_accounts_router
from aureus_backend.api.v1.ingestion.banking import router as banking_ingestion_router

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Aureus Backend",
    description="Backend API for Aureus wealth tracker",
    version="0.1.0",
    debug=True  # Enable debug mode
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(google_auth_router, prefix="/api/v1/auth")
app.include_router(credentials_router, prefix="/api/v1/auth")
app.include_router(banking_banks_router, prefix="/api/v1")
app.include_router(banking_connect_router, prefix="/api/v1")
app.include_router(banking_accounts_router, prefix="/api/v1")
app.include_router(banking_ingestion_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
