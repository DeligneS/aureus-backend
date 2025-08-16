"""API endpoints for managing API credentials."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from aureus_backend.repositories.api_credentials import ApiCredentialsRepository
from aureus_backend.utils.dependencies import get_current_user, get_db_session

router = APIRouter(prefix="/auth/credentials", tags=["auth"])

class CredentialResponse(BaseModel):
    """Response model for API credential details."""
    id: int
    provider: str
    provider_uid: str
    expires_at: datetime
    is_expired: bool

@router.get("/", response_model=list[CredentialResponse])
def list_credentials(
    provider: Optional[str] = None,
    user_id: UUID = Depends(get_current_user),
    db_session = Depends(get_db_session)
):
    """
    List all API credentials for the current user.
    
    Args:
        provider: Optional provider filter
        user_id: Current user's ID
        db_session: Database session
        
    Returns:
        List of API credentials
    """
    cred_repo = ApiCredentialsRepository(db_session)
    credentials = cred_repo.list_by_user_provider(user_id, provider)
    
    now = datetime.utcnow()
    return [
        CredentialResponse(
            id=cred.id,
            provider=cred.provider,
            provider_uid=cred.provider_uid,
            expires_at=cred.expires_at,
            is_expired=cred.expires_at <= now
        )
        for cred in credentials
    ]

@router.delete("/{credential_id}")
def delete_credential(
    credential_id: int,
    user_id: UUID = Depends(get_current_user),
    db_session = Depends(get_db_session)
):
    """
    Delete an API credential.
    
    Args:
        credential_id: ID of the credential to delete
        user_id: Current user's ID
        db_session: Database session
        
    Returns:
        Success message
    """
    cred_repo = ApiCredentialsRepository(db_session)
    deleted = cred_repo.delete(credential_id, user_id)
    
    if not deleted:
        raise HTTPException(404, "Credential not found")
    
    return {"message": "Credential deleted successfully"} 