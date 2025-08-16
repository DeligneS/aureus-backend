from pathlib import Path
import os
import urllib.parse

from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "sandbox")

    # Base directory
    BASE_DIR: Path = Path(__file__).parent.parent.parent.parent
    SECRETS_DIR: Path = BASE_DIR / ".secrets" / ENVIRONMENT

    # Find the .pem file and extract application_id from filename
    enable_banking_private_key_file: Path = next(SECRETS_DIR.glob("*.pem"))
    enable_banking_application_id: str = enable_banking_private_key_file.stem
    enable_banking_private_key: str = enable_banking_private_key_file.read_text()

    # Supabase connection string
    connection_string: str = (
        f"postgresql://postgres.{os.environ.get('SUPABASE_PROJECT_REF')}:"
        f"{urllib.parse.quote(os.environ.get('SUPABASE_DB_PASSWORD'))}@"
        f"{os.environ.get('SUPABASE_REGION')}.pooler.supabase.com:6543/postgres"
    )
