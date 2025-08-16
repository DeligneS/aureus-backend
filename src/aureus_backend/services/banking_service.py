from datetime import datetime, timezone, timedelta
from typing import Optional

from aureus_backend.clients.enable_banking import EnableBankingClient


class BankingService:
    def __init__(self):
        self.client = EnableBankingClient()
        self._app_details = None
    
    async def get_auth_url(self, bank_name: str, bank_country: str) -> dict:
        """Get the authorization URL for a specific bank."""
        if not self._app_details:
            self._app_details = self.client.get_application_details()
            
        redirect_url = self._app_details["redirect_urls"][0]
        auth_data = self.client.start_authorization(
            aspsp_name=bank_name,
            aspsp_country=bank_country,
            redirect_url=redirect_url
        )
        return {
            "auth_url": auth_data["url"],
            "state": auth_data.get("state")
        }
    
    async def create_session(self, auth_code: str) -> dict:
        """Create a new banking session using the authorization code."""
        return self.client.create_session(auth_code)
    
    async def get_session_details(self, session_id: str) -> dict:
        """Get details for a specific session."""
        return self.client.get_session(session_id)
    
    async def get_account_balances(self, account_uid: str) -> dict:
        """Get balances for a specific account."""
        return self.client.get_account_balances(account_uid)
    
    async def get_account_transactions(
        self, 
        account_uid: str, 
        days_back: int = 90,
        continuation_key: Optional[str] = None
    ) -> dict:
        """Get transactions for a specific account."""
        date_from = (datetime.now(timezone.utc) - timedelta(days=days_back)).date().isoformat()
        return self.client.get_account_transactions(
            account_uid=account_uid,
            date_from=date_from,
            continuation_key=continuation_key
        )
    
    async def get_available_banks(self) -> list:
        """Get list of available banks."""
        return self.client.get_available_aspsps()
