import dlt
from datetime import datetime, timedelta
from typing import Generator, Any
from aureus_backend.clients import EnableBankingClient
from aureus_backend.core import Config

@dlt.resource(
    write_disposition="append",
    name="raw_transactions",
    primary_key=["entry_reference", "user_id"]
)
def enable_banking_transactions(
    client: EnableBankingClient,
    user_id: str,
    lookback_days: int = 90
) -> Generator[dict[str, Any], None, None]:
    """Resource that yields Enable Banking transactions with user context.
    
    Args:
        client: Initialized Enable Banking client
        user_id: The user ID to associate transactions with
        lookback_days: How many days of history to fetch
    """
    # Get all accounts for the user's session
    session = client.get_session(Config.get_user_session_id(user_id))
    
    date_from = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    
    for account in session["accounts"]:
        account_uid = account["uid"]
        
        # Paginate through all transactions
        continuation_key = None
        while True:
            response = client.get_account_transactions(
                account_uid=account_uid,
                date_from=date_from,
                continuation_key=continuation_key
            )
            
            # Enrich each transaction with user and account context
            for transaction in response["transactions"]:
                transaction["user_id"] = user_id
                transaction["account_uid"] = account_uid
                transaction["account_name"] = account.get("name")
                transaction["account_iban"] = account.get("iban")
                transaction["ingested_at"] = datetime.utcnow().isoformat()
                
                yield transaction
            
            # Handle pagination
            continuation_key = response.get("continuation_key")
            if not continuation_key:
                break

def run_enable_banking_pipeline(user_id: str) -> 'dlt.pipeline.LoadInfo':
    """Run the Enable Banking pipeline for a specific user.
    
    Args:
        user_id: The user to run the pipeline for
        
    Returns:
        LoadInfo containing pipeline run statistics
    """
    # Initialize pipeline with Supabase destination
    pipeline = dlt.pipeline(
        pipeline_name=f"enable_banking_{user_id}",
        destination='postgres',
        dataset_name="raw_enable_banking",
        credentials={
            "connection_string": Config.connection_string
        }
    )

    # Initialize client with user's credentials
    client = EnableBankingClient()

    # Load data
    info = pipeline.run(
        enable_banking_transactions(
            client=client,
            user_id=user_id
        )
    )
    
    return info
