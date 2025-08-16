"""Bank account management endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from aureus_backend.clients import EnableBankingClient
from aureus_backend.utils.dependencies import get_current_user

router = APIRouter(prefix="/banking/accounts", tags=["banking"])

@router.get("/{account_uid}/balances")
async def get_account_balances(
    account_uid: str,
    user_id: UUID = Depends(get_current_user),
    banking_service = Depends(EnableBankingClient)
):
    """Get balances for a specific account."""
    try:
        return await banking_service.get_account_balances(account_uid)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{account_uid}/transactions")
async def get_account_transactions(
    account_uid: str,
    days_back: int = 90,
    continuation_key: str = None,
    user_id: UUID = Depends(get_current_user),
    banking_service = Depends(EnableBankingClient)
):
    """Get transactions for a specific account."""
    try:
        return await banking_service.get_account_transactions(
            account_uid=account_uid,
            days_back=days_back,
            continuation_key=continuation_key
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 