"""Bank information endpoints."""
from fastapi import APIRouter, Depends, HTTPException

from aureus_backend.clients import EnableBankingClient

router = APIRouter(prefix="/banking/banks", tags=["banking"])

@router.get("")
def list_available_banks(
    banking_service = Depends(EnableBankingClient)
):
    """
    List all available banks that can be connected.
    
    Returns:
        List of available banks with their details
    """
    try:
        banks = banking_service.get_available_aspsps()
        return {"banks": banks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
