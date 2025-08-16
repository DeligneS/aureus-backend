"""Repository for managing API credentials in the database."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from ..models.api_credentials import ApiCredential
from ..utils.crypto import enc, dec

class ApiCredentialsRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        user_id: UUID,
        provider: str,
        provider_uid: str,
        access_token: str,
        refresh_token: Optional[str],
        expires_at: datetime
    ) -> ApiCredential:
        """Create or update API credentials."""
        # Encrypt tokens
        encrypted_access = enc(access_token)
        encrypted_refresh = enc(refresh_token) if refresh_token else None
        
        # Try to find existing credentials
        stmt = select(ApiCredential).where(
            and_(
                ApiCredential.user_id == user_id,
                ApiCredential.provider == provider,
                ApiCredential.provider_uid == provider_uid
            )
        )
        existing = self.session.execute(stmt).scalar_one_or_none()
        
        if existing:
            # Update existing record
            existing.access_token = encrypted_access
            existing.refresh_token = encrypted_refresh
            existing.expires_at = expires_at
            existing.updated_at = datetime.utcnow()
            self.session.flush()
            return existing
            
        # Create new record
        cred = ApiCredential(
            user_id=user_id,
            provider=provider,
            provider_uid=provider_uid,
            access_token=encrypted_access,
            refresh_token=encrypted_refresh,
            expires_at=expires_at
        )
        self.session.add(cred)
        self.session.flush()
        return cred

    def get(
        self,
        user_id: UUID,
        provider: str,
        provider_uid: str
    ) -> Optional[ApiCredential]:
        """Get API credentials by user_id, provider and provider_uid."""
        stmt = select(ApiCredential).where(
            and_(
                ApiCredential.user_id == user_id,
                ApiCredential.provider == provider,
                ApiCredential.provider_uid == provider_uid
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def list_by_user_provider(
        self,
        user_id: UUID,
        provider: Optional[str] = None
    ) -> list[ApiCredential]:
        """List all API credentials for a user, optionally filtered by provider."""
        conditions = [ApiCredential.user_id == user_id]
        if provider:
            conditions.append(ApiCredential.provider == provider)
            
        stmt = select(ApiCredential).where(and_(*conditions))
        return list(self.session.execute(stmt).scalars().all())

    def delete(self, credential_id: int, user_id: UUID) -> bool:
        """Delete API credentials by ID, ensuring it belongs to the specified user."""
        stmt = select(ApiCredential).where(
            and_(
                ApiCredential.id == credential_id,
                ApiCredential.user_id == user_id
            )
        )
        cred = self.session.execute(stmt).scalar_one_or_none()
        
        if not cred:
            return False
            
        self.session.delete(cred)
        self.session.flush()
        return True

    def decrypt_tokens(self, cred: ApiCredential) -> tuple[str, Optional[str]]:
        """Decrypt access and refresh tokens from an ApiCredential instance."""
        return dec(cred.access_token), dec(cred.refresh_token)
