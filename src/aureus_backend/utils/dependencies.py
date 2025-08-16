"""FastAPI dependency utilities."""
from typing import Generator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import jwt

from ..core.config import Config

# Create database engine with Supabase-specific settings
engine = create_engine(
    Config.connection_string,
    echo=Config.ENVIRONMENT == "development",
    pool_size=5,
    max_overflow=10,
    connect_args={
        "sslmode": "require"  # Required for Supabase
    },
    # Disable prepared statements as they are not supported in transaction mode
    execution_options={
        "prepared_statement_cache_size": 0
    }
)

# Create session factory
SessionLocal = sessionmaker(
    engine,
    expire_on_commit=False
)

# JWT auth scheme
auth_scheme = HTTPBearer()

def get_db_session() -> Generator[Session, None, None]:
    """Get a database session for the request."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def get_current_user(
    auth: HTTPAuthorizationCredentials = Depends(auth_scheme)
) -> UUID:
    """Get the current authenticated user's ID from the JWT token."""
    try:
        payload = jwt.decode(
            auth.credentials,
            Config.jwt_secret,
            algorithms=["HS256"]
        )
        return UUID(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        ) from e
