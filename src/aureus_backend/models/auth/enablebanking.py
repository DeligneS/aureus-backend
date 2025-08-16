from pydantic import BaseModel

class StartAuthRequest(BaseModel):
    """Request model for starting Enable Banking authorization."""
    aspsp_id: str
    aspsp_country: str
    redirect_url: str
