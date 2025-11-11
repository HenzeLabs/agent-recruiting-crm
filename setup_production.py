#!/usr/bin/env python3
"""
Production configuration and deployment script
"""
import os
import sqlite3
from datetime import datetime

def setup_production():
    """Setup production environment"""
    
    # Ensure database exists and is optimized
    if not os.path.exists('db.sqlite3'):
        print("Creating production database...")
        from app import init_db
        init_db()
    
    # Optimize database for production
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Create indexes for better performance
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_recruits_stage ON recruits(stage)",
        "CREATE INDEX IF NOT EXISTS idx_recruits_updated ON recruits(updated_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_mentors_status ON mentors(status)",
        "CREATE INDEX IF NOT EXISTS idx_meetings_date ON meetings(meeting_date)",
        "CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status)"
    ]
    
    for index in indexes:
        try:
            cursor.execute(index)
            print(f"✓ Created index: {index.split('idx_')[1].split(' ')[0]}")
        except sqlite3.Error as e:
            print(f"Index creation warning: {e}")
    
    # Optimize database settings
    cursor.execute("PRAGMA optimize")
    cursor.execute("VACUUM")
    
    conn.commit()
    conn.close()
    
    print("✅ Production setup complete!")
    print("\nRecommended environment variables:")
    print("export FLASK_ENV=production")
    print("export SECRET_KEY='your-secret-key-here'")
    print("export PORT=5000")

if __name__ == "__main__":
    setup_production()