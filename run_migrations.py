from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import urllib.parse
from pathlib import Path

def run_migrations():
    # Load environment variables
    load_dotenv()
    
    try:
        # Get connection string components for Supavisor transaction mode
        project_ref = os.environ.get("SUPABASE_PROJECT_REF")
        password = os.environ.get("SUPABASE_DB_PASSWORD")
        region = "aws-0-eu-west-3"  # EU West 3 (Paris) region
        
        # Use Supavisor transaction mode connection string
        connection_string = f"postgresql://postgres.{project_ref}:{urllib.parse.quote(password)}@{region}.pooler.supabase.com:6543/postgres"
        
        print("Running migrations...")
        
        # Create engine with SSL mode require and disable prepared statements
        engine = create_engine(
            connection_string,
            connect_args={
                "sslmode": "require"
            },
            execution_options={
                "prepared_statement_cache_size": 0
            }
        )
        
        # Get all migration files in order
        migrations_dir = Path('src/aureus_backend/migrations')
        migration_files = sorted(migrations_dir.glob('*.sql'))
        
        # Execute each migration file
        with engine.connect() as connection:
            for migration_file in migration_files:
                print(f"\nApplying migration: {migration_file.name}")
                
                # Read the migration SQL file
                migration_sql = migration_file.read_text()
                
                # Start transaction for this migration
                with connection.begin():
                    # Split and execute multiple statements if present
                    for statement in migration_sql.split(';'):
                        if statement.strip():
                            connection.execute(text(statement))
                
                print(f"✅ Successfully applied {migration_file.name}")
            
            print("\n✅ All migrations completed successfully!")
            
            # Show created tables and their RLS status
            result = connection.execute(text("""
                select 
                    t.table_name,
                    obj_description((quote_ident(t.table_schema) || '.' || quote_ident(t.table_name))::regclass) as description,
                    has_table_privilege(t.table_name, 'select') as has_select,
                    has_table_privilege(t.table_name, 'insert') as has_insert
                from information_schema.tables t
                where t.table_schema = 'public'
                  and t.table_type = 'BASE TABLE'
            """))
            tables = result.fetchall()
            print("\nTables in database:")
            for table in tables:
                print(f"- {table[0]}")
                if table[1]:  # If there's a description
                    print(f"  Description: {table[1]}")
                print(f"  Permissions: select={table[2]}, insert={table[3]}")
            
            return True
            
    except Exception as e:
        print("\n❌ Error running migrations:")
        print(str(e))
        return False

if __name__ == "__main__":
    run_migrations()
