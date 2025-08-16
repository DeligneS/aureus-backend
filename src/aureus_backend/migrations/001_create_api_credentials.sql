-- Create users table if it doesn't exist
create table if not exists users (
    id uuid primary key,
    email varchar not null unique,
    created_at timestamp with time zone default current_timestamp,
    updated_at timestamp with time zone default current_timestamp
);

-- Create api_credentials table for secure token storage
create table if not exists api_credentials (
    id serial primary key,
    user_id uuid not null references users(id),
    provider varchar not null,              -- 'enablebanking', 'binance', etc.
    provider_uid varchar not null,          -- 'cbc_be', 'binance-main'
    access_token varchar not null,          -- AES-encrypted
    refresh_token varchar,                  -- AES-encrypted (NULL for API keys)
    expires_at timestamp with time zone not null,
    created_at timestamp with time zone default current_timestamp,
    updated_at timestamp with time zone default current_timestamp,
    constraint api_credentials_unique unique (user_id, provider, provider_uid)
);

-- Create index for quick lookups by user_id and provider
create index if not exists idx_api_credentials_user_provider 
    on api_credentials(user_id, provider);

-- Add a comment to the table
comment on table api_credentials is 'Stores encrypted API credentials and tokens for various providers'; 