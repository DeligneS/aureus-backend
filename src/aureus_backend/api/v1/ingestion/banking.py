"""Banking data ingestion endpoints."""
from datetime import datetime, timezone, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import dlt

from aureus_backend.clients import EnableBankingClient
from aureus_backend.repositories.api_credentials import ApiCredentialsRepository
from aureus_backend.utils.dependencies import get_current_user, get_db_session
from aureus_backend.core.config import Config

router = APIRouter(prefix="/ingestion/banking", tags=["ingestion"])

@router.post("")
def ingest_enablebanking(
    user_id: UUID = Depends(get_current_user),
    db_session: Session = Depends(get_db_session)
):
    """Ingest Enable Banking data for all connected banks."""
    cred_repo = ApiCredentialsRepository(db_session)
    credentials = cred_repo.list_by_user_provider(user_id, "enablebanking")
    
    if not credentials:
        raise HTTPException(404, "No Enable Banking credentials found")
    
    total_transactions = 0
    processed_banks = 0
    client = EnableBankingClient()
    
    for cred in credentials:
        # Get bank session details
        session = client.get_session(cred.provider_uid)
        
        # Verify session is still authorized
        if session["status"] != "AUTHORIZED":
            continue
            
        # Get transactions for each account (last 90 days)
        date_from = (datetime.now(timezone.utc) - timedelta(days=90)).date().isoformat()
        
        # Create DLT pipeline for this bank
        pipeline = dlt.pipeline(
            pipeline_name=f"enablebanking_{user_id}_{cred.provider_uid}",
            destination="postgres",
            dataset_name="raw_enablebanking",
            credentials={
                "connection_string": Config.connection_string
            }
        )
        
        # Process each account
        for account in session["accounts"]:
            account_uid = account["uid"]
            
            # Get transactions with pagination
            continuation_key = None
            while True:
                response = client.get_account_transactions(
                    account_uid=account_uid,
                    date_from=date_from,
                    continuation_key=continuation_key
                )
                
                # Enrich transactions with context
                for transaction in response["transactions"]:
                    transaction["user_id"] = str(user_id)
                    transaction["account_uid"] = account_uid
                    transaction["account_name"] = account.get("name")
                    transaction["account_iban"] = account.get("iban")
                    transaction["ingested_at"] = datetime.utcnow().isoformat()
                    
                    total_transactions += 1
                
                # Load transactions into database
                pipeline.run(response["transactions"])
                
                # Handle pagination
                continuation_key = response.get("continuation_key")
                if not continuation_key:
                    break
        
        processed_banks += 1
    
    return {
        "message": "Ingestion completed successfully",
        "stats": {
            "processed_banks": processed_banks,
            "total_transactions": total_transactions
        }
    } 