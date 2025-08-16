from datetime import datetime, timezone, timedelta
import uuid
import requests
import jwt as pyjwt

from ..core import Config


class EnableBankingClient:
    """Client for interacting with the Enable Banking API.
    
    This client handles all direct API interactions with Enable Banking, including:
    - Authentication via JWT
    - Bank (ASPSP) discovery
    - Account authorization
    - Account information retrieval (balances, transactions)
    
    The client automatically handles JWT generation and token refresh.
    Authentication is done using the private key file (.pem) stored in the secrets directory.
    """
    
    API_ORIGIN = "https://api.enablebanking.com"
    
    def __init__(self):
        """Initialize the client with authentication headers."""
        self.base_headers = {"Authorization": f"Bearer {self._generate_jwt()}"}
    
    def _generate_jwt(self) -> str:
        """Generate a JWT token for API authentication.
        
        The token is valid for 1 hour and includes:
        - Application ID (kid) from the .pem filename
        - Standard claims (iss, aud, iat, exp)
        - RS256 signature using the private key
        
        Returns:
            str: The generated JWT token
        """
        iat = int(datetime.now().timestamp())
        jwt_body = {
            "iss": "enablebanking.com",
            "aud": "api.enablebanking.com",
            "iat": iat,
            "exp": iat + 3600,
        }
        return pyjwt.encode(
            jwt_body,
            Config.enable_banking_private_key,
            algorithm="RS256",
            headers={"kid": Config.enable_banking_application_id},
        )
    
    def get_application_details(self) -> dict:
        """Get details about the registered Enable Banking application.
        
        Returns:
            dict: Application details including redirect URLs and other settings
        
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        response = requests.get(f"{self.API_ORIGIN}/application", headers=self.base_headers)
        response.raise_for_status()
        return response.json()
    
    def get_available_aspsps(self) -> list:
        """Get list of available banks (ASPSPs - Account Servicing Payment Service Providers).
        
        Returns:
            list: List of available banks with their details (name, country, etc.)
        
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        response = requests.get(f"{self.API_ORIGIN}/aspsps", headers=self.base_headers)
        response.raise_for_status()
        return response.json()["aspsps"]
    
    def start_authorization(self, aspsp_name: str, aspsp_country: str, redirect_url: str) -> dict:
        """Start the bank authorization process for a specific bank.
        
        This initiates the OAuth flow where the user will be redirected to their bank
        to authorize access to their account information.
        
        Args:
            aspsp_name: Name of the bank (e.g., "Nordea")
            aspsp_country: Two-letter country code (e.g., "FI" for Finland)
            redirect_url: URL where the user will be redirected after authorization
        
        Returns:
            dict: Authorization details including the URL where the user should be redirected
        
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        body = {
            "access": {
                "valid_until": (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
            },
            "aspsp": {"name": aspsp_name, "country": aspsp_country},
            "state": str(uuid.uuid4()),
            "redirect_url": redirect_url,
            "psu_type": "personal",
        }
        response = requests.post(f"{self.API_ORIGIN}/auth", json=body, headers=self.base_headers)
        response.raise_for_status()
        return response.json()
    
    def create_session(self, auth_code: str) -> dict:
        """Create a new banking session using the authorization code.
        
        Args:
            auth_code: The authorization code received after user authorization
        
        Returns:
            dict: Session details including session ID and authorized accounts
        
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        response = requests.post(
            f"{self.API_ORIGIN}/sessions", 
            json={"code": auth_code}, 
            headers=self.base_headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_session(self, session_id: str) -> dict:
        """Get details of an existing banking session.
        
        Args:
            session_id: ID of the session to retrieve
        
        Returns:
            dict: Session details including authorized accounts
        
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        response = requests.get(
            f"{self.API_ORIGIN}/sessions/{session_id}", 
            headers=self.base_headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_account_balances(self, account_uid: str) -> dict:
        """Get balances for a specific bank account.
        
        Args:
            account_uid: Unique identifier of the account
        
        Returns:
            dict: Account balances information
        
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        response = requests.get(
            f"{self.API_ORIGIN}/accounts/{account_uid}/balances", 
            headers=self.base_headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_account_transactions(self, account_uid: str, date_from: str, continuation_key: str = None) -> dict:
        """Get transactions for a specific bank account.
        
        Args:
            account_uid: Unique identifier of the account
            date_from: Start date for transactions in ISO format (YYYY-MM-DD)
            continuation_key: Optional key for paginated results
        
        Returns:
            dict: Account transactions with optional continuation key for pagination
        
        Raises:
            requests.exceptions.HTTPError: If the API request fails
        """
        query = {"date_from": date_from}
        if continuation_key:
            query["continuation_key"] = continuation_key
            
        response = requests.get(
            f"{self.API_ORIGIN}/accounts/{account_uid}/transactions",
            params=query,
            headers=self.base_headers,
        )
        response.raise_for_status()
        return response.json()
