"""Google authentication models."""
from pydantic import BaseModel, Field

class AuthRequest(BaseModel):
    """Authentication request with authorization code."""
    code: str = Field(..., description="Authorization code from Google OAuth")

class AuthResponse(BaseModel):
    """Authentication response with access token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: dict = Field(
        ...,
        description="Basic user info from Google (email, name, picture)",
        example={
            "email": "user@example.com",
            "name": "John Doe",
            "picture": "https://..."
        }
    ) 