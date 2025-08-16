# Aureus Backend

Backend service for Aureus wealth tracker, featuring banking integration with Enable Banking.

## TODO

1. Ingestions
   1. Setup (Supabase connection)
   2. Enable Banking
   3. Trade Republic
   4. Bitget
   5. Binance
2. Transformation
   1. DBT project setup
   2. Connection with Supabase
   3. Transformations raw -> staging -> intermediate -> mart (core / reporting)

## Setup

1. Make sure you have Python 3.10+ and Poetry installed
2. Clone the repository
3. Install dependencies:

    ```bash
    uv sync
    uv install
    ```

4. Add your Enable Banking private key:
   - Create a `secrets` directory in the project root
   - Place your Enable Banking private key file (`.pem` file) in the `secrets` directory
   - The filename of your .pem file should be your application ID from Enable Banking (e.g., `aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee.pem`)

## Running the Application

1. Activate the virtual environment:

    ```bash
    uv shell
    ```

2. Run the FastAPI application:

    ```bash
    uvicorn aureus_backend.main:app --reload --host localhost --port 8000 --log-level debug
    ```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:

- Swagger UI documentation at `http://localhost:8000/docs`
- ReDoc documentation at `http://localhost:8000/redoc`

## Available Endpoints

### Banking API (`/api/v1/banking`)

- `POST /auth-url` - Get authorization URL for bank connection
- `POST /sessions` - Create a new banking session
- `GET /sessions/{session_id}` - Get session details
- `GET /accounts/{account_uid}/balances` - Get account balances
- `POST /accounts/{account_uid}/transactions` - Get account transactions
- `GET /banks` - Get list of available banks

## Development

The project follows a clean architecture pattern:

- `api/` - API endpoints and request/response models
- `services/` - Business logic layer
- `clients/` - External API clients (Enable Banking)
- `core/` - Core configuration and utilities

## Enable Banking Integration

This project uses Enable Banking for accessing bank account information. To get started:

1. Sign up for an Enable Banking account at https://enablebanking.com
2. Register a new application in the Enable Banking Control Panel
3. Download your private key file (it will be named with your application ID, e.g., `aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee.pem`)
4. Place the .pem file in the `secrets` directory

The application will automatically use your private key file for authentication with Enable Banking's API.

## Environment Variables

The following environment variables are required to run the application:

### Database Settings
- `DATABASE_URL`: PostgreSQL connection URL (format: `postgresql+asyncpg://user:password@host:port/dbname`)
- `SQL_DEBUG`: Enable SQL query logging (optional, default: false)
- `DB_POOL_SIZE`: Database connection pool size (optional, default: 5)
- `DB_MAX_OVERFLOW`: Maximum number of connections above pool size (optional, default: 10)

### Enable Banking Integration
- `ENABLE_BANKING_CLIENT_ID`: Your Enable Banking client ID
- `ENABLE_BANKING_PRIVATE_KEY`: Your Enable Banking private key

Create a `.env` file in the project root with these variables before running the application.
