import sys, os
from dotenv import load_dotenv

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath(os.path.join("backend", "src")))

load_dotenv(".env")
from database.database import get_db1

conn = get_db1()
try:
    with conn.cursor() as cur:
        cur.execute("UPDATE tickets SET ticket_status = 'NEW' WHERE confirmed = True AND ticket_status = 'draft'")
        print(f"Fixed {cur.rowcount} tickets.")
    conn.commit()
finally:
    conn.close()
