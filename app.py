from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_compress import Compress
import sqlite3, os, logging
from datetime import datetime, timezone, timedelta
from contextlib import contextmanager
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['COMPRESS_MIMETYPES'] = [
    'text/html', 'text/css', 'text/xml', 'application/json',
    'application/javascript', 'text/javascript'
]

# Enable compression
Compress(app)
DB_FILE = "db.sqlite3"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = None
    try:
        conn = sqlite3.connect(DB_FILE, timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL')  # Better concurrency
        yield conn
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def handle_db_error(f):
    """Decorator for handling database errors"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except sqlite3.Error as e:
            logger.error(f"Database error in {f.__name__}: {e}")
            return jsonify({"error": "Database error"}), 500
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            return jsonify({"error": "Internal server error"}), 500
    return decorated_function

def validate_recruit_data(data):
    """Validate recruit data"""
    if not data.get('name', '').strip():
        return False, "Name is required"
    return True, None

def get_overdue_recruits():
    """Get recruits who need follow-up (>3 days since last contact)"""
    with get_db() as conn:
        from datetime import timedelta
        three_days_ago = datetime.now(timezone.utc) - timedelta(days=3)
        recruits = conn.execute("""
            SELECT * FROM recruits 
            WHERE stage NOT IN ('Licensed', 'Inactive') 
            AND (last_contact IS NULL OR last_contact < ?)
            ORDER BY priority DESC, updated_at ASC
        """, (three_days_ago,)).fetchall()
        return [dict_from_row(r) for r in recruits]

def mark_contact(recruit_id, message_type='manual', content=''):
    """Mark contact made with recruit"""
    with get_db() as conn:
        now = datetime.now(timezone.utc)
        conn.execute(
            "UPDATE recruits SET last_contact = ?, updated_at = ? WHERE id = ?",
            (now, now, recruit_id)
        )
        if content:
            conn.execute(
                "INSERT INTO communications (recruit_id, message_type, content) VALUES (?, ?, ?)",
                (recruit_id, message_type, content)
            )
        conn.commit()

def dict_from_row(row):
    """Convert sqlite3.Row to dictionary"""
    return dict(zip(row.keys(), row))

# ---------- Routes ----------
@app.route("/")
@handle_db_error
def dashboard():
    with get_db() as conn:
        # Get all recruits with overdue flags
        recruits_rows = conn.execute("""
            SELECT *,
                CASE WHEN last_contact IS NULL OR
                     datetime(last_contact) < datetime('now', '-3 days')
                     AND stage NOT IN ('Licensed', 'Inactive')
                THEN 1 ELSE 0 END as is_overdue
            FROM recruits
            ORDER BY is_overdue DESC, priority DESC, updated_at DESC
        """).fetchall()
        logger.info(f"Dashboard: Found {len(recruits_rows)} recruits in {DB_FILE}")

        # Convert sqlite3.Row objects to dictionaries
        recruits = [dict_from_row(r) for r in recruits_rows]

        stages = ["New", "Contacted", "In Training", "Licensed", "Inactive"]
        counts = {s: sum(1 for r in recruits if r["stage"]==s) for s in stages}

        # Get overdue count
        overdue_count = sum(1 for r in recruits if r['is_overdue'])

        # Get weekly stats
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        weekly_new = conn.execute(
            "SELECT COUNT(*) FROM recruits WHERE created_at > ?", (week_ago,)
        ).fetchone()[0]

        weekly_licensed = conn.execute(
            "SELECT COUNT(*) FROM recruits WHERE stage = 'Licensed' AND updated_at > ?", (week_ago,)
        ).fetchone()[0]

    return render_template("dashboard.html",
                         recruits=recruits,
                         counts=counts,
                         stages=stages,
                         overdue_count=overdue_count,
                         weekly_new=weekly_new,
                         weekly_licensed=weekly_licensed)

@app.route("/add", methods=["GET","POST"])
@handle_db_error
def add():
    if request.method=="POST":
        name = request.form.get("name", "").strip()
        if not name:
            return render_template("add.html", error="Name is required"), 400
        
        now = datetime.now(timezone.utc)
        with get_db() as conn:
            conn.execute("""
                INSERT INTO recruits (name, email, phone, stage, notes, source, last_contact, created_at, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                request.form.get("email", "").strip(),
                request.form.get("phone", "").strip(),
                request.form.get("stage", "New"),
                request.form.get("notes", "").strip(),
                request.form.get('source', 'Manual'),
                None,
                now,
                now
            ))
            conn.commit()
        return redirect(url_for("dashboard"))
    return render_template("add.html")

@app.route("/update/<int:id>", methods=["POST"])
@handle_db_error
def update(id):
    stage = request.form.get("stage", "New")
    notes = request.form.get("notes", "").strip()
    
    with get_db() as conn:
        # Check if stage changed to mark contact
        old_stage = conn.execute("SELECT stage FROM recruits WHERE id=?", (id,)).fetchone()
        if old_stage and old_stage[0] != stage:
            mark_contact(id, 'stage_change', f'Stage changed to {stage}')
        
        conn.execute(
            "UPDATE recruits SET stage=?, notes=?, updated_at=? WHERE id=?", 
            (stage, notes, datetime.now(timezone.utc), id)
        )
        conn.commit()
    return redirect(url_for("dashboard"))

@app.route("/delete/<int:id>")
@handle_db_error
def delete(id):
    with get_db() as conn:
        conn.execute("DELETE FROM recruits WHERE id=?", (id,))
        conn.commit()
    return redirect(url_for("dashboard"))

# ---------- API Endpoints for AJAX ----------

# Recruits API
@app.route("/api/recruits", methods=["GET", "POST"])
@handle_db_error
def api_recruits():
    if request.method == "GET":
        with get_db() as conn:
            recruits = conn.execute("SELECT * FROM recruits ORDER BY updated_at DESC").fetchall()
            return jsonify([dict_from_row(r) for r in recruits])
    
    elif request.method == "POST":
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        valid, error = validate_recruit_data(data)
        if not valid:
            return jsonify({"error": error}), 400
            
        with get_db() as conn:
            now = datetime.now(timezone.utc)
            conn.execute("""
                INSERT INTO recruits (name, email, phone, stage, notes, source, last_contact, updated_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (data['name'], data.get('email'), data.get('phone'),
                  data.get('stage', 'New'), data.get('notes'), data.get('source', 'Manual'),
                  None, now, now))
            conn.commit()
            # Force WAL checkpoint to ensure data is visible immediately
            conn.execute('PRAGMA wal_checkpoint(FULL)')
            new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            recruit = conn.execute("SELECT * FROM recruits WHERE id=?", (new_id,)).fetchone()
            logger.info(f"Created recruit {new_id}: {data['name']}")
            return jsonify(dict_from_row(recruit)), 201

@app.route("/api/recruits/<int:id>", methods=["GET", "PUT", "DELETE"])
@handle_db_error
def api_recruit(id):
    if request.method == "GET":
        with get_db() as conn:
            recruit = conn.execute("SELECT * FROM recruits WHERE id=?", (id,)).fetchone()
            if recruit:
                return jsonify(dict_from_row(recruit))
            return jsonify({"error": "Not found"}), 404
    
    elif request.method == "PUT":
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        with get_db() as conn:
            # Check if recruit exists
            existing = conn.execute("SELECT id FROM recruits WHERE id=?", (id,)).fetchone()
            if not existing:
                return jsonify({"error": "Not found"}), 404
                
            conn.execute("""
                UPDATE recruits 
                SET name=?, email=?, phone=?, stage=?, notes=?, updated_at=?
                WHERE id=?
            """, (data['name'], data.get('email'), data.get('phone'), 
                  data['stage'], data.get('notes'), datetime.now(timezone.utc), id))
            conn.commit()
            recruit = conn.execute("SELECT * FROM recruits WHERE id=?", (id,)).fetchone()
            return jsonify(dict_from_row(recruit))
    
    elif request.method == "DELETE":
        with get_db() as conn:
            result = conn.execute("DELETE FROM recruits WHERE id=?", (id,))
            conn.commit()
            if result.rowcount == 0:
                return jsonify({"error": "Not found"}), 404
            return jsonify({"success": True})

# Follow-up and Communication APIs
@app.route("/api/overdue")
@handle_db_error
def api_overdue():
    """Get overdue recruits needing follow-up"""
    overdue = get_overdue_recruits()
    return jsonify(overdue)

@app.route("/api/contact/<int:recruit_id>", methods=["POST"])
@handle_db_error
def api_mark_contact(recruit_id):
    """Mark contact made with recruit"""
    data = request.get_json() or {}
    message_type = data.get('type', 'manual')
    content = data.get('content', '')
    
    mark_contact(recruit_id, message_type, content)
    return jsonify({"success": True})

@app.route("/api/templates")
@handle_db_error
def api_templates():
    """Get message templates"""
    with get_db() as conn:
        templates = conn.execute("SELECT * FROM message_templates ORDER BY stage, name").fetchall()
        return jsonify([dict_from_row(t) for t in templates])

@app.route("/api/quick-message", methods=["POST"])
@handle_db_error
def api_quick_message():
    """Send quick follow-up message"""
    data = request.get_json()
    recruit_id = data.get('recruit_id')
    template_id = data.get('template_id')
    custom_message = data.get('message')
    
    with get_db() as conn:
        if template_id:
            template = conn.execute("SELECT content FROM message_templates WHERE id=?", (template_id,)).fetchone()
            recruit = conn.execute("SELECT name FROM recruits WHERE id=?", (recruit_id,)).fetchone()
            if template and recruit:
                message = template[0].format(name=recruit[0])
            else:
                return jsonify({"error": "Template or recruit not found"}), 404
        else:
            message = custom_message
        
        mark_contact(recruit_id, 'quick_message', message)
        return jsonify({"success": True, "message": message})

# Mentors API
@app.route("/api/mentors", methods=["GET", "POST"])
@handle_db_error
def api_mentors():
    if request.method == "GET":
        with get_db() as conn:
            mentors = conn.execute("SELECT * FROM mentors ORDER BY updated_at DESC").fetchall()
            return jsonify([dict_from_row(m) for m in mentors])
    
    elif request.method == "POST":
        data = request.get_json()
        with get_db() as conn:
            conn.execute("""
                INSERT INTO mentors (name, email, phone, specialty, status, notes, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (data['name'], data.get('email'), data.get('phone'), 
                  data.get('specialty'), data.get('status', 'Active'), data.get('notes'), datetime.now(timezone.utc)))
            conn.commit()
            new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            mentor = conn.execute("SELECT * FROM mentors WHERE id=?", (new_id,)).fetchone()
            return jsonify(dict_from_row(mentor)), 201

@app.route("/api/mentors/<int:id>", methods=["GET", "PUT", "DELETE"])
@handle_db_error
def api_mentor(id):
    if request.method == "GET":
        with get_db() as conn:
            mentor = conn.execute("SELECT * FROM mentors WHERE id=?", (id,)).fetchone()
            if mentor:
                return jsonify(dict_from_row(mentor))
            return jsonify({"error": "Not found"}), 404
    
    elif request.method == "PUT":
        data = request.get_json()
        with get_db() as conn:
            conn.execute("""
                UPDATE mentors 
                SET name=?, email=?, phone=?, specialty=?, status=?, notes=?, updated_at=?
                WHERE id=?
            """, (data['name'], data.get('email'), data.get('phone'), 
                  data.get('specialty'), data.get('status'), data.get('notes'), datetime.now(timezone.utc), id))
            conn.commit()
            mentor = conn.execute("SELECT * FROM mentors WHERE id=?", (id,)).fetchone()
            return jsonify(dict_from_row(mentor))
    
    elif request.method == "DELETE":
        with get_db() as conn:
            conn.execute("DELETE FROM mentors WHERE id=?", (id,))
            conn.commit()
            return jsonify({"success": True})

# Meetings API
@app.route("/api/meetings", methods=["GET", "POST"])
@handle_db_error
def api_meetings():
    if request.method == "GET":
        with get_db() as conn:
            meetings = conn.execute("""
                SELECT m.*, r.name as recruit_name, mt.name as mentor_name
                FROM meetings m
                LEFT JOIN recruits r ON m.recruit_id = r.id
                LEFT JOIN mentors mt ON m.mentor_id = mt.id
                ORDER BY m.meeting_date DESC
            """).fetchall()
            return jsonify([dict_from_row(m) for m in meetings])
    
    elif request.method == "POST":
        data = request.get_json()
        with get_db() as conn:
            conn.execute("""
                INSERT INTO meetings (title, recruit_id, mentor_id, meeting_date, status, notes, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (data['title'], data.get('recruit_id'), data.get('mentor_id'), 
                  data.get('meeting_date'), data.get('status', 'Scheduled'), data.get('notes'), datetime.now(timezone.utc)))
            conn.commit()
            new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            meeting = conn.execute("SELECT * FROM meetings WHERE id=?", (new_id,)).fetchone()
            return jsonify(dict_from_row(meeting)), 201

@app.route("/api/meetings/<int:id>", methods=["GET", "PUT", "DELETE"])
@handle_db_error
def api_meeting(id):
    if request.method == "PUT":
        data = request.get_json()
        with get_db() as conn:
            conn.execute("""
                UPDATE meetings 
                SET title=?, recruit_id=?, mentor_id=?, meeting_date=?, status=?, notes=?, updated_at=?
                WHERE id=?
            """, (data['title'], data.get('recruit_id'), data.get('mentor_id'), 
                  data.get('meeting_date'), data.get('status'), data.get('notes'), datetime.now(timezone.utc), id))
            conn.commit()
            meeting = conn.execute("SELECT * FROM meetings WHERE id=?", (id,)).fetchone()
            return jsonify(dict_from_row(meeting))
    
    elif request.method == "DELETE":
        with get_db() as conn:
            conn.execute("DELETE FROM meetings WHERE id=?", (id,))
            conn.commit()
            return jsonify({"success": True})

# Goals API
@app.route("/api/goals", methods=["GET", "POST"])
@handle_db_error
def api_goals():
    if request.method == "GET":
        with get_db() as conn:
            goals = conn.execute("SELECT * FROM goals ORDER BY target_date ASC").fetchall()
            return jsonify([dict_from_row(g) for g in goals])
    
    elif request.method == "POST":
        data = request.get_json()
        with get_db() as conn:
            conn.execute("""
                INSERT INTO goals (title, description, target_date, status, progress, updated_at) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data['title'], data.get('description'), data.get('target_date'), 
                  data.get('status', 'Not Started'), data.get('progress', 0), datetime.now(timezone.utc)))
            conn.commit()
            new_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
            goal = conn.execute("SELECT * FROM goals WHERE id=?", (new_id,)).fetchone()
            return jsonify(dict_from_row(goal)), 201

@app.route("/api/goals/<int:id>", methods=["GET", "PUT", "DELETE"])
@handle_db_error
def api_goal(id):
    if request.method == "PUT":
        data = request.get_json()
        with get_db() as conn:
            conn.execute("""
                UPDATE goals 
                SET title=?, description=?, target_date=?, status=?, progress=?, updated_at=?
                WHERE id=?
            """, (data['title'], data.get('description'), data.get('target_date'), 
                  data.get('status'), data.get('progress', 0), datetime.now(timezone.utc), id))
            conn.commit()
            goal = conn.execute("SELECT * FROM goals WHERE id=?", (id,)).fetchone()
            return jsonify(dict_from_row(goal))
    
    elif request.method == "DELETE":
        with get_db() as conn:
            conn.execute("DELETE FROM goals WHERE id=?", (id,))
            conn.commit()
            return jsonify({"success": True})

# ---------- Init DB ----------
def init_db():
    with get_db() as conn:
        # Recruits table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS recruits(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                stage TEXT DEFAULT 'New',
                notes TEXT,
                source TEXT DEFAULT 'Manual',
                priority INTEGER DEFAULT 1,
                last_contact TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Communications table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS communications(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recruit_id INTEGER,
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
        
        # Mentors table
        conn.execute("""
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
        
        # Meetings table
        conn.execute("""
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
        
        # Goals table
        conn.execute("""
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
        
        # Add missing columns to existing tables if they don't exist
        try:
            conn.execute("ALTER TABLE recruits ADD COLUMN source TEXT DEFAULT 'Manual'")
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        try:
            conn.execute("ALTER TABLE recruits ADD COLUMN priority INTEGER DEFAULT 1")
        except sqlite3.OperationalError:
            pass  # Column already exists
            
        try:
            conn.execute("ALTER TABLE recruits ADD COLUMN last_contact TIMESTAMP")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
        conn.commit()

# Add route for service worker
@app.route('/sw.js')
def service_worker():
    response = app.send_static_file('sw.js')
    response.headers['Cache-Control'] = 'no-cache'
    return response

# Add route for logo
@app.route('/logo.png')
def logo():
    from flask import send_from_directory
    return send_from_directory('.', 'logo.png')

# Add caching headers for static assets
@app.after_request
def add_header(response):
    if request.endpoint == 'static':
        response.headers['Cache-Control'] = 'public, max-age=31536000'  # 1 year
    return response

if __name__ == "__main__":
    init_db()
    # Only enable debug in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
