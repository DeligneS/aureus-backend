"""Bank connection endpoints."""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from aureus_backend.clients import EnableBankingClient
from aureus_backend.repositories.api_credentials import ApiCredentialsRepository
from aureus_backend.utils.dependencies import get_current_user, get_db_session

router = APIRouter(prefix="/banking/connect", tags=["banking"])

class BankAuthRequest(BaseModel):
    bank_name: str
    bank_country: str

@router.post("/auth-url")
async def get_auth_url(
    request: BankAuthRequest,
    banking_service = Depends(EnableBankingClient)
):
    """Get authorization URL for bank connection."""
    try:
        return await banking_service.get_auth_url(
            bank_name=request.bank_name,
            bank_country=request.bank_country
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/callback")
def handle_callback(
    code: str,
    user_id: UUID = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    Handle callback from Enable Banking after user authorization.
    
    Args:
        code: Authorization code from Enable Banking
        user_id: Current user's ID
        db_session: Database session
        
    Returns:
        Success message with bank details
    """
    client = EnableBankingClient()
    cred_repo = ApiCredentialsRepository(db_session)
    
    # Exchange code for session
    session = client.create_session(code)
    if not session or "session_id" not in session:
        raise HTTPException(400, "Failed to create Enable Banking session")
    
    # Get session details
    session_details = client.get_session(session["session_id"])
    if session_details["status"] != "AUTHORIZED":
        raise HTTPException(400, "Bank authorization failed or was cancelled")
    
    # Extract bank info
    bank = session_details["aspsp"]
    bank_id = f"{bank['name']}_{bank['country']}".lower()
    
    # Calculate expiry from access details
    access = session_details["access"]
    expires_at = datetime.fromisoformat(access["valid_until"].replace("Z", "+00:00"))
    
    # Store credentials
    cred_repo.create(
        user_id=user_id,
        provider="enablebanking",
        provider_uid=bank_id,
        access_token=session["access_token"],
        refresh_token=session.get("refresh_token"),
        expires_at=expires_at
    )
    
    return {
        "message": "Bank connected successfully",
        "bank": {
            "name": bank["name"],
            "country": bank["country"],
            "account_count": len(session_details["accounts"]),
            "expires_at": expires_at.isoformat()
        }
    }

@router.get("/connections")
def list_connections(
    user_id: UUID = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """
    List all active bank connections for the user.
    
    Args:
        user_id: Current user's ID
        db_session: Database session
        
    Returns:
        List of connected banks with their status
    """
    client = EnableBankingClient()
    cred_repo = ApiCredentialsRepository(db_session)
    
    # Get all Enable Banking credentials
    credentials = cred_repo.list_by_user_provider(user_id, "enablebanking")
    
    connections = []
    for cred in credentials:
        try:
            # Get session details
            session = client.get_session(cred.provider_uid)
            
            # Add connection info
            connections.append({
                "bank": {
                    "name": session["aspsp"]["name"],
                    "country": session["aspsp"]["country"]
                },
                "status": session["status"],
                "account_count": len(session["accounts"]),
                "expires_at": session["access"]["valid_until"],
                "last_update": session["authorized"]
            })
        except Exception:
            # Skip failed connections
            continue
    
    return {"connections": connections}
