import os
import psycopg2

def create_tables():
    neon_url = os.environ.get("NEON_DB_URL")
    if not neon_url:
        print("Error: NEON_DB_URL not set.")
        return
    
    conn = psycopg2.connect(neon_url)
    cur = conn.cursor()
    
    tables_sql = """
    CREATE TABLE IF NOT EXISTS sessions (
        session_id VARCHAR(50) PRIMARY KEY,
        channel VARCHAR(20),
        language VARCHAR(10),
        caller_number VARCHAR(20),
        session_status VARCHAR(20),
        ticket_id VARCHAR(50),
        ended_at TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id VARCHAR(50) PRIMARY KEY,
        session_id VARCHAR(50),
        ticket_status VARCHAR(20),
        channel VARCHAR(20),
        category VARCHAR(50),
        location TEXT,
        description TEXT,
        severity VARCHAR(20),
        caller_name VARCHAR(100),
        phone_number VARCHAR(20),
        confirmed BOOLEAN DEFAULT FALSE,
        updated_at TIMESTAMP,
        mode VARCHAR(50),
        _category_conf FLOAT,
        raw_issue_text TEXT
    );

    CREATE TABLE IF NOT EXISTS tts_results (
        id SERIAL PRIMARY KEY,
        session_id VARCHAR(50),
        turn INTEGER,
        question_text TEXT
    );

    CREATE TABLE IF NOT EXISTS recordings (
        recording_id VARCHAR(50) PRIMARY KEY,
        session_id VARCHAR(50),
        ticket_id VARCHAR(50),
        merged_audio_path TEXT
    );

    CREATE TABLE IF NOT EXISTS recording_turns (
        id SERIAL PRIMARY KEY,
        recording_id VARCHAR(50),
        session_id VARCHAR(50),
        turn INTEGER,
        transcript TEXT,
        stt_audio_file_path TEXT,
        tts_question TEXT
    );
    """
    
    try:
        cur.execute(tables_sql)
        conn.commit()
        print("Successfully created required tables in Neon DB.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    create_tables()
