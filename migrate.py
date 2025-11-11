#!/usr/bin/env python3
"""
Migration script to update the database schema
"""
import sqlite3
import os

DB_FILE = "db.sqlite3"

def migrate():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("Starting migration...")
    
    # Check if updated_at column exists in recruits table
    cursor.execute("PRAGMA table_info(recruits)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'updated_at' not in columns:
        print("Adding updated_at and created_at columns to recruits table...")
        cursor.execute("ALTER TABLE recruits ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        cursor.execute("ALTER TABLE recruits ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        print("✓ Columns added to recruits table")
    else:
        print("✓ Recruits table already has timestamp columns")
    
    # Create new tables if they don't exist
    print("Creating new tables if needed...")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mentors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            specialty TEXT,
            status TEXT DEFAULT 'Active',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Mentors table ready")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meetings(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            recruit_id INTEGER,
            mentor_id INTEGER,
            meeting_date TEXT,
            status TEXT DEFAULT 'Scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recruit_id) REFERENCES recruits(id),
            FOREIGN KEY (mentor_id) REFERENCES mentors(id)
        )
    """)
    print("✓ Meetings table ready")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            target_date TEXT,
            status TEXT DEFAULT 'Not Started',
            progress INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✓ Goals table ready")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        print(f"Database file {DB_FILE} not found. Run the app first to create it.")
    else:
        migrate()
