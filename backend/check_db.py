import sqlite3

def check_schema():
    conn = sqlite3.connect('sermon_extraction.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(video_jobs)")
    columns = cursor.fetchall()
    for col in columns:
        print(col)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
    if cursor.fetchone():
        cursor.execute("SELECT version_num FROM alembic_version")
        print("Alembic version:", cursor.fetchone())
    else:
        print("alembic_version table does not exist")
    
    conn.close()

if __name__ == "__main__":
    check_schema()
