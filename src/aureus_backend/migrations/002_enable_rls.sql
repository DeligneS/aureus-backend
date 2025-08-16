-- Enable RLS on tables
alter table users enable row level security;
alter table api_credentials enable row level security;

-- Create policies for users table
create policy "Users can view their own data"
    on users
    for select
    using (auth.uid() = id);

create policy "Users can update their own data"
    on users
    for update
    using (auth.uid() = id);

-- Create policies for api_credentials table
create policy "Users can view their own credentials"
    on api_credentials
    for select
    using (auth.uid() = user_id);

create policy "Users can insert their own credentials"
    on api_credentials
    for insert
    with check (auth.uid() = user_id);

create policy "Users can update their own credentials"
    on api_credentials
    for update
    using (auth.uid() = user_id);

create policy "Users can delete their own credentials"
    on api_credentials
    for delete
    using (auth.uid() = user_id);

-- Add comment explaining RLS setup
comment on table users is 'User profiles with RLS enabled - users can only access their own data';
comment on table api_credentials is 'API credentials with RLS enabled - users can only access their own credentials'; 