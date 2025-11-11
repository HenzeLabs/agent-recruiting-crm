#!/usr/bin/env python3
"""
Add comprehensive demo data for testing AutoMentor CRM
Simulates real-world recruiting scenarios with various data patterns
"""
import sqlite3
import random
from datetime import datetime, timedelta, timezone

DB_FILE = "db.sqlite3"

# Sample data pools
FIRST_NAMES = ["Sarah", "Mike", "Lisa", "David", "Emma", "James", "Maria", "John", 
               "Jennifer", "Robert", "Patricia", "Michael", "Linda", "William", "Barbara",
               "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Karen", "Charles"]
LAST_NAMES = ["Johnson", "Chen", "Rodriguez", "Kim", "Wilson", "Brown", "Garcia", "Miller", 
              "Davis", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Anderson", "Taylor",
              "Thomas", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White"]
DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "email.com"]
STAGES = ["New", "Contacted", "In Training", "Licensed", "Inactive"]
SOURCES = ["Referral", "Company Portal", "Self-Generated", "Social Media", "Email Campaign", 
           "LinkedIn", "Indeed", "Job Fair", "Website", "Phone Call"]

NOTES_TEMPLATES = [
    "Very interested in agency opportunity",
    "Has insurance background - worked at {company}",
    "Referred by {referrer}",
    "Follow up next week about licensing",
    "Needs to complete state exam",
    "Strong sales background - {years} years experience",
    "Currently working full-time, looking to transition",
    "Responded to {source} ad",
    "Met at networking event",
    "Excited about remote work opportunity",
    "Requires flexible schedule for family",
    "Previous experience in financial services",
    "Bilingual - Spanish/English advantage",
    "Looking for passive income opportunity",
    "Completed pre-licensing course",
    "Scheduled for state exam on {date}",
    "Licensed in multiple states",
    "Ready to start immediately",
    ""  # Some with no notes
]

COMPANIES = ["State Farm", "Allstate", "Farmers", "Progressive", "Liberty Mutual", 
             "Nationwide", "GEICO", "MetLife"]

def generate_phone():
    """Generate realistic US phone number"""
    return f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}"

def generate_email(first, last, allow_duplicate=False):
    """Generate email from name"""
    first_clean = first.lower().replace(" ", "")
    last_clean = last.lower().replace(" ", "")
    suffix = "" if allow_duplicate else str(random.randint(1, 999))
    return f"{first_clean}.{last_clean}{suffix}@{random.choice(DOMAINS)}"

def generate_notes():
    """Generate random notes"""
    template = random.choice(NOTES_TEMPLATES)
    return template.format(
        company=random.choice(COMPANIES),
        referrer=random.choice(FIRST_NAMES),
        years=random.randint(2, 15),
        source=random.choice(SOURCES),
        date=f"{random.randint(1,28)}/{random.randint(1,12)}/2025"
    )

def add_demo_data():
    """Add comprehensive demo data to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("🎭 Adding comprehensive demo data to AutoMentor CRM...\n")
    print("=" * 60)
    
    # Check if we should clear existing data
    cursor.execute("SELECT COUNT(*) FROM recruits")
    existing_count = cursor.fetchone()[0]
    
    if existing_count > 0:
        response = input(f"\n⚠️  Found {existing_count} existing recruits. Clear all data? (y/n): ")
        if response.lower() == 'y':
            cursor.execute("DELETE FROM recruits")
            print("✓ Cleared existing recruits\n")
    
    recruits_added = 0
    now = datetime.now(timezone.utc)
    
    # ========== Test Level 1: Intake - Data Entry ==========
    print("\n📝 LEVEL 1: INTAKE - DATA ENTRY")
    print("-" * 60)
    
    # 15 complete records with all fields
    print("Adding 15 complete records...")
    for _ in range(15):
        first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = generate_email(first, last)
        phone = generate_phone()
        stage = random.choice(STAGES)
        notes = generate_notes()
        source = random.choice(SOURCES)
        
        days_ago = random.randint(1, 45)
        created_at = now - timedelta(days=days_ago)
        updated_at = created_at + timedelta(days=random.randint(0, min(7, days_ago)))
        last_contact = updated_at if random.random() > 0.3 else None
        
        cursor.execute("""
            INSERT INTO recruits (name, email, phone, stage, notes, source, 
                                last_contact, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, stage, notes, source, last_contact, created_at, updated_at))
        recruits_added += 1
    print(f"✓ Added 15 complete records\n")
    
    # 10 partial records (missing email or phone)
    print("Adding 10 partial records (missing fields)...")
    for _ in range(10):
        first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = generate_email(first, last) if random.random() > 0.4 else ""
        phone = generate_phone() if random.random() > 0.4 else ""
        stage = random.choice(STAGES[:3])  # Usually early stages
        notes = generate_notes() if random.random() > 0.5 else ""
        source = random.choice(SOURCES)
        
        created_at = now - timedelta(days=random.randint(1, 14))
        updated_at = created_at
        
        cursor.execute("""
            INSERT INTO recruits (name, email, phone, stage, notes, source, 
                                created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, stage, notes, source, created_at, updated_at))
        recruits_added += 1
    print(f"✓ Added 10 partial records\n")
    
    # 5 minimal records (name only)
    print("Adding 5 minimal records (name only)...")
    for _ in range(5):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        created_at = now - timedelta(days=random.randint(0, 3))
        
        cursor.execute("""
            INSERT INTO recruits (name, stage, source, created_at, updated_at)
            VALUES (?, 'New', 'Manual', ?, ?)
        """, (name, created_at, created_at))
        recruits_added += 1
    print(f"✓ Added 5 minimal records\n")
    
    # ========== Test Level 2: Stage Transitions ==========
    print("\n🔄 LEVEL 2: STAGE TRANSITIONS")
    print("-" * 60)
    
    # Add recruits at each stage with realistic progression
    stage_progression = [
        ("New", 8, 0, 2),
        ("Contacted", 7, 3, 10),
        ("In Training", 5, 7, 25),
        ("Licensed", 6, 20, 60),
        ("Inactive", 4, 30, 90)
    ]
    
    for stage, count, min_days, max_days in stage_progression:
        print(f"Adding {count} recruits in '{stage}' stage...")
        for _ in range(count):
            first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
            name = f"{first} {last}"
            email = generate_email(first, last)
            phone = generate_phone()
            notes = generate_notes()
            source = random.choice(SOURCES)
            
            days_ago = random.randint(min_days, max_days)
            created_at = now - timedelta(days=days_ago)
            updated_at = created_at + timedelta(days=random.randint(min_days, min(days_ago, max_days)))
            last_contact = updated_at if stage != "New" else None
            
            cursor.execute("""
                INSERT INTO recruits (name, email, phone, stage, notes, source, 
                                    last_contact, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, email, phone, stage, notes, source, last_contact, created_at, updated_at))
            recruits_added += 1
    print(f"✓ Added stage progression records\n")
    
    # ========== Test Level 3: Follow-Up Logic ==========
    print("\n⏰ LEVEL 3: FOLLOW-UP LOGIC")
    print("-" * 60)
    
    # Add 8 recruits needing follow-up (>3 days old, not Licensed/Inactive)
    print("Adding 8 recruits needing follow-up (>3 days no contact)...")
    for _ in range(8):
        first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = generate_email(first, last)
        phone = generate_phone()
        stage = random.choice(["New", "Contacted", "In Training"])
        notes = f"⚠️ OVERDUE: Last contact {random.randint(4, 14)} days ago"
        source = random.choice(SOURCES)
        
        days_stale = random.randint(4, 14)
        old_contact = now - timedelta(days=days_stale)
        created_at = now - timedelta(days=days_stale + 5)
        
        cursor.execute("""
            INSERT INTO recruits (name, email, phone, stage, notes, source, 
                                last_contact, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, stage, notes, source, old_contact, created_at, old_contact))
        recruits_added += 1
    print(f"✓ Added 8 overdue recruits\n")
    
    # ========== Test Level 4: Edge Cases ==========
    print("\n🔬 LEVEL 4: EDGE CASES")
    print("-" * 60)
    
    # Duplicate emails
    print("Adding 3 recruits with duplicate emails...")
    duplicate_email = "duplicate.test@gmail.com"
    for i in range(3):
        name = f"Duplicate Test {i+1}"
        cursor.execute("""
            INSERT INTO recruits (name, email, phone, stage, notes, source, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, duplicate_email, generate_phone(), random.choice(STAGES), 
              f"Duplicate email test case {i+1}", "Manual", now, now))
        recruits_added += 1
    print(f"✓ Added duplicate email records\n")
    
    # Invalid/unusual data
    print("Adding 5 edge case records...")
    edge_cases = [
        ("Invalid Email Format", "not-an-email", generate_phone(), "New", "Invalid email test"),
        ("No Contact Info", "", "", "Contacted", "Missing all contact details"),
        ("Very Long Name Testing UI Boundaries And Word Wrapping", "long@test.com", 
         generate_phone(), "In Training", "Long name UI test"),
        ("Licensed→Contacted Revert", "revert@test.com", generate_phone(), "Contacted", 
         "Was licensed, moved back (unusual workflow)"),
        ("Special Characters @#$%", "special@test.com", "(000) 000-0000", "New", 
         "Special character handling test")
    ]
    
    for name, email, phone, stage, notes in edge_cases:
        cursor.execute("""
            INSERT INTO recruits (name, email, phone, stage, notes, source, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, phone, stage, notes, "Manual", now, now))
        recruits_added += 1
    print(f"✓ Added edge case records\n")
    
    # ========== Test Level 5: Stress Test Data ==========
    print("\n💪 LEVEL 5: STRESS TEST DATA")
    print("-" * 60)
    
    # Add many more records to reach 100+ total
    cursor.execute("SELECT COUNT(*) FROM recruits")
    current_count = cursor.fetchone()[0]
    remaining = max(0, 100 - current_count)
    
    if remaining > 0:
        print(f"Adding {remaining} additional records to reach 100+ total...")
        for _ in range(remaining):
            first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
            name = f"{first} {last}"
            email = generate_email(first, last)
            phone = generate_phone()
            stage = random.choice(STAGES)
            notes = generate_notes()
            source = random.choice(SOURCES)
            
            days_ago = random.randint(1, 90)
            created_at = now - timedelta(days=days_ago)
            updated_at = created_at + timedelta(days=random.randint(0, min(30, days_ago)))
            last_contact = updated_at if random.random() > 0.4 else None
            
            cursor.execute("""
                INSERT INTO recruits (name, email, phone, stage, notes, source, 
                                    last_contact, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, email, phone, stage, notes, source, last_contact, created_at, updated_at))
            recruits_added += 1
        print(f"✓ Added {remaining} stress test records\n")
    
    conn.commit()
    
    # ========== Summary ==========
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    cursor.execute("SELECT COUNT(*) FROM recruits")
    total = cursor.fetchone()[0]
    print(f"\n✅ Total Recruits in Database: {total}")
    print(f"📝 Records Added This Run: {recruits_added}")
    
    print("\n📈 Distribution by Stage:")
    cursor.execute("""
        SELECT stage, COUNT(*) as count 
        FROM recruits 
        GROUP BY stage 
        ORDER BY 
            CASE stage
                WHEN 'New' THEN 1
                WHEN 'Contacted' THEN 2
                WHEN 'In Training' THEN 3
                WHEN 'Licensed' THEN 4
                WHEN 'Inactive' THEN 5
            END
    """)
    for stage, count in cursor.fetchall():
        percentage = (count / total * 100) if total > 0 else 0
        bar = "█" * int(count / 2)
        print(f"  {stage:15} {count:3} ({percentage:5.1f}%) {bar}")
    
    print("\n📅 Contact Recency:")
    cursor.execute("""
        SELECT 
            CASE 
                WHEN last_contact IS NULL THEN 'Never Contacted'
                WHEN julianday('now') - julianday(last_contact) <= 3 THEN 'Recent (≤3 days)'
                WHEN julianday('now') - julianday(last_contact) <= 7 THEN 'Active (4-7 days)'
                WHEN julianday('now') - julianday(last_contact) <= 30 THEN 'Aging (8-30 days)'
                ELSE 'Stale (>30 days)'
            END as recency,
            COUNT(*) as count
        FROM recruits
        GROUP BY recency
        ORDER BY 
            CASE recency
                WHEN 'Recent (≤3 days)' THEN 1
                WHEN 'Active (4-7 days)' THEN 2
                WHEN 'Aging (8-30 days)' THEN 3
                WHEN 'Stale (>30 days)' THEN 4
                WHEN 'Never Contacted' THEN 5
            END
    """)
    for recency, count in cursor.fetchall():
        print(f"  {recency:20} {count:3}")
    
    print("\n⚠️  Follow-Up Needed:")
    cursor.execute("""
        SELECT COUNT(*) FROM recruits
        WHERE stage NOT IN ('Licensed', 'Inactive')
        AND (last_contact IS NULL OR julianday('now') - julianday(last_contact) > 3)
    """)
    overdue = cursor.fetchone()[0]
    print(f"  {overdue} recruits need immediate attention")
    
    print("\n📧 Data Completeness:")
    cursor.execute("SELECT COUNT(*) FROM recruits WHERE email IS NOT NULL AND email != ''")
    with_email = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM recruits WHERE phone IS NOT NULL AND phone != ''")
    with_phone = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM recruits WHERE notes IS NOT NULL AND notes != ''")
    with_notes = cursor.fetchone()[0]
    
    print(f"  With Email: {with_email} ({with_email/total*100:.1f}%)")
    print(f"  With Phone: {with_phone} ({with_phone/total*100:.1f}%)")
    print(f"  With Notes: {with_notes} ({with_notes/total*100:.1f}%)")
    
    print("\n" + "=" * 60)
    print("✅ Demo data generation complete!")
    print("🚀 Ready for testing - start the server and run tests")
    print("=" * 60 + "\n")
    
    conn.close()

if __name__ == "__main__":
    add_demo_data()