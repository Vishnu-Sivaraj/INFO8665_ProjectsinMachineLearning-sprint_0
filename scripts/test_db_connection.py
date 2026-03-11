import os
import psycopg2
import sys

# Add the project root to the path so src can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_connection():
    neon_url = os.environ.get("NEON_DB_URL")
    if not neon_url:
        print("Error: NEON_DB_URL environment variable is not set.")
        return False

    print("Attempting to connect to Neon DB...")
    
    try:
        conn = psycopg2.connect(neon_url)
        print("Successfully connected to Neon DB!")
        
        with conn.cursor() as cur:
            # Check for required tables
            tables = ['sessions', 'tickets', 'tts_results', 'recordings', 'recording_turns']
            
            print("\nChecking table structures:")
            for table in tables:
                try:
                    cur.execute(f"SELECT count(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"  OK {table}: {count} rows")
                except psycopg2.Error as e:
                    print(f"  FAIL {table}: Table might not exist or error occurred - {e.pgerror.strip()}")
                    conn.rollback() # Important to rollback the transaction block after an error
                    continue
            
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
