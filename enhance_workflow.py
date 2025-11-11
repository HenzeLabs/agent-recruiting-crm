#!/usr/bin/env python3
"""
Enhanced migration for Gina's recruiting workflow
"""
import sqlite3
import os
from datetime import datetime, timedelta

DB_FILE = "db.sqlite3"

def enhance_for_gina():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("Enhancing CRM for Gina's workflow...")
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(recruits)")
    existing_cols = [col[1] for col in cursor.fetchall()]
    
    # Add new columns for Gina's workflow
    new_columns = [
        ("source", "TEXT DEFAULT 'Unknown'"),
        ("last_contact", "TIMESTAMP"),
        ("next_action", "TEXT"),
        ("response_time", "INTEGER DEFAULT 0"),
        ("next_meeting", "TEXT"),
        ("license_status", "TEXT DEFAULT 'Not Started'"),
        ("priority", "INTEGER DEFAULT 0")
    ]
    
    for col_name, col_def in new_columns:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE recruits ADD COLUMN {col_name} {col_def}")
            print(f"✓ Added {col_name} column")
    
    # Update stage values to match Gina's process
    cursor.execute("""
        UPDATE recruits 
        SET stage = CASE 
            WHEN stage = 'New' THEN 'New'
            WHEN stage = 'Contacted' THEN 'Contacted'
            WHEN stage = 'Interview' THEN 'In Training'
            WHEN stage = 'Licensed' THEN 'Licensed'
            ELSE 'Inactive'
        END
    """)
    
    # Create communications log table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS communications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recruit_id INTEGER NOT NULL,
            message_type TEXT DEFAULT 'manual',
            content TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recruit_id) REFERENCES recruits(id)
        )
    """)
    print("✓ Created communications table")
    
    # Create follow-up templates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS message_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            stage TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert default templates
    templates = [
        ("Initial Follow-up", "Hi {name}! Just checking in - did you get a chance to look at the pre-licensing info I sent? Let me know if you have any questions!", "New"),
        ("Training Check", "Hey {name}! How's the pre-licensing course going? Any questions I can help with?", "Contacted"),
        ("Exam Reminder", "Hi {name}! Ready to schedule your licensing exam? I'm here to help with next steps!", "In Training"),
        ("Welcome Licensed", "Congratulations {name}! Welcome to the team. Let's schedule your onboarding call.", "Licensed")
    ]
    
    for name, content, stage in templates:
        cursor.execute("""
            INSERT OR IGNORE INTO message_templates (name, content, stage) 
            VALUES (?, ?, ?)
        """, (name, content, stage))
    
    print("✓ Added message templates")
    
    conn.commit()
    conn.close()
    print("✅ Enhanced for Gina's workflow!")

if __name__ == "__main__":
    enhance_for_gina()