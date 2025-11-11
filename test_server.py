#!/usr/bin/env python3
"""Test server wrapper for Playwright tests."""
import os
import sqlite3

# Clean up old test database if it exists
if os.path.exists('test_db.sqlite3'):
    os.remove('test_db.sqlite3')

# Create fresh test database with complete schema
conn = sqlite3.connect('test_db.sqlite3')

# Recruits table - matches current app schema
conn.execute("""
    CREATE TABLE recruits(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        stage TEXT DEFAULT 'New',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        source TEXT DEFAULT 'Unknown',
        last_contact TIMESTAMP,
        next_action TEXT,
        response_time INTEGER DEFAULT 0,
        next_meeting TEXT,
        license_status TEXT DEFAULT 'Not Started',
        priority INTEGER DEFAULT 0
    )
""")

# Communications table for tracking messages
conn.execute("""
    CREATE TABLE IF NOT EXISTS communications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recruit_id INTEGER NOT NULL,
        message_type TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (recruit_id) REFERENCES recruits(id)
    )
""")

# Message templates table
conn.execute("""
    CREATE TABLE IF NOT EXISTS message_templates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stage TEXT,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# Add some default message templates for testing
conn.execute("""
    INSERT INTO message_templates (name, stage, content) VALUES
    ('Initial Contact', 'New', 'Hi {name}, thanks for your interest in joining our team!'),
    ('Follow-up', 'Contacted', 'Hi {name}, just checking in on your application.'),
    ('Training Reminder', 'In Training', 'Hi {name}, reminder about your training session.')
""")

conn.commit()
conn.close()

# Import and patch app to use test database
import app as app_module
app_module.DB_FILE = 'test_db.sqlite3'

if __name__ == '__main__':
    # Run the Flask app
    app_module.app.run(debug=False, port=5001, host='127.0.0.1')
