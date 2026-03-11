# src/database/database.py
# PostgreSQL database connection and CRUD operations
# DB1: insight311          → sessions, tickets, tts_results
# DB2: insight311_recordings → recordings, recording_turns

import psycopg2
import psycopg2.extras
import os
from datetime import datetime, date



DB1_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "insight311",
    "user":     "postgres",
    "password": "741741" 
}

DB2_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "insight311_recordings",
    "user":     "postgres",
    "password": "741741"  
}

def serialize(obj):
    if isinstance(obj, dict):
        return {k: serialize(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize(i) for i in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.strftime("%Y-%m-%dT%H:%M:%S")
    return obj

def get_db_connection(config_fallback):
    neon_url = os.environ.get("NEON_DB_URL")
    if neon_url:
        return psycopg2.connect(neon_url)
    return psycopg2.connect(**config_fallback)

def get_db1():
    return get_db_connection(DB1_CONFIG)

def get_db2():
    return get_db_connection(DB2_CONFIG)


# ── Sessions ──────────────────────────────────────────────────────
def save_session(session_id, channel, language="en", caller_number=None):
    conn = get_db1()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO sessions
                    (session_id, channel, language, caller_number, session_status)
                VALUES (%s, %s, %s, %s, 'active')
            """, (session_id, channel, language, caller_number))
        conn.commit()
    finally:
        conn.close()

def get_session(session_id):
    conn = get_db1()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM sessions WHERE session_id = %s", (session_id,))
            return cur.fetchone()
    finally:
        conn.close()

def update_session(session_id, updates: dict):
    conn = get_db1()
    try:
        with conn.cursor() as cur:
            for key, value in updates.items():
                cur.execute(
                    f"UPDATE sessions SET {key} = %s WHERE session_id = %s",
                    (value, session_id)
                )
        conn.commit()
    finally:
        conn.close()


# ── Tickets ───────────────────────────────────────────────────────
def save_ticket(ticket_id, session_id, channel):
    conn = get_db1()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tickets (ticket_id, session_id, ticket_status, channel)
                VALUES (%s, %s, 'draft', %s)
            """, (ticket_id, session_id, channel))
        conn.commit()
    finally:
        conn.close()

def get_ticket(ticket_id):
    conn = get_db1()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM tickets WHERE ticket_id = %s", (ticket_id,))
            row = cur.fetchone()
            if row:
                t = dict(row)
                t["ticketNumber"] = t.get("ticket_id")
                t["name"] = t.get("caller_name")
                t["phone"] = t.get("phone_number")
                t["status"] = t.get("ticket_status")
                t["createdAt"] = t.get("updated_at")
                if not t.get("description"):
                    t["description"] = t.get("raw_issue_text")
                return t
            return None
    finally:
        conn.close()

def get_all_tickets(ticket_status=None, channel=None):
    conn = get_db1()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            query  = "SELECT * FROM tickets WHERE 1=1"
            params = []
            if ticket_status:
                query += " AND ticket_status = %s"
                params.append(ticket_status)
            if channel:
                query += " AND channel = %s"
                params.append(channel)
            cur.execute(query, params)
            rows = cur.fetchall()
            
            # Map DB columns to frontend React component expectations
            mapped = []
            for r in rows:
                t = dict(r)
                t["ticketNumber"] = t.get("ticket_id")
                t["name"] = t.get("caller_name")
                t["phone"] = t.get("phone_number")
                t["status"] = t.get("ticket_status")
                t["createdAt"] = t.get("updated_at")
                if not t.get("description"):
                    t["description"] = t.get("raw_issue_text")
                mapped.append(t)
            return mapped
    finally:
        conn.close()

def update_ticket(ticket_id, updates: dict):
    conn = get_db1()
    try:
        with conn.cursor() as cur:
            for key, value in updates.items():
                cur.execute(
                    f"UPDATE tickets SET {key} = %s WHERE ticket_id = %s",
                    (value, ticket_id)
                )
            cur.execute(
                "UPDATE tickets SET updated_at = %s WHERE ticket_id = %s",
                (datetime.utcnow(), ticket_id)
            )
        conn.commit()
    finally:
        conn.close()


# ── TTS Results ───────────────────────────────────────────────────
def save_tts_result(session_id, turn, question_text):
    conn = get_db1()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tts_results (session_id, turn, question_text)
                VALUES (%s, %s, %s)
            """, (session_id, turn, question_text))
        conn.commit()
    finally:
        conn.close()


# ── Recordings (DB2) ──────────────────────────────────────────────
def save_recording(recording_id, session_id, ticket_id, merged_audio_path):
    conn = get_db2()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO recordings
                    (recording_id, session_id, ticket_id, merged_audio_path)
                VALUES (%s, %s, %s, %s)
            """, (recording_id, session_id, ticket_id, merged_audio_path))
        conn.commit()
    finally:
        conn.close()

def save_recording_turn(recording_id, session_id, turn,
                        transcript, stt_audio_file_path, tts_question):
    conn = get_db2()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO recording_turns
                    (recording_id, session_id, turn,
                     transcript, stt_audio_file_path, tts_question)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (recording_id, session_id, turn,
                  transcript, stt_audio_file_path, tts_question))
        conn.commit()
    finally:
        conn.close()

def get_recording(recording_id):
    conn = get_db2()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM recordings WHERE recording_id = %s",
                (recording_id,)
            )
            recording = cur.fetchone()
            if recording:
                cur.execute("""
                    SELECT * FROM recording_turns
                    WHERE recording_id = %s ORDER BY turn
                """, (recording_id,))
                recording = dict(recording)
                recording["turns"] = cur.fetchall()
            return recording
    finally:
        conn.close()

def delete_recording(recording_id):
    conn = get_db2()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM recording_turns WHERE recording_id = %s",
                (recording_id,)
            )
            cur.execute(
                "DELETE FROM recordings WHERE recording_id = %s",
                (recording_id,)
            )
        conn.commit()
    finally:
        conn.close()
