import sqlite3
import uuid
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

import os

# Use /tmp on Vercel since the root is read-only
if os.environ.get('VERCEL'):
    DB_NAME = "/tmp/users.db"
else:
    DB_NAME = "users.db"


def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # 1. Create table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT,
                full_name TEXT,
                avatar_url TEXT,
                plan_type TEXT DEFAULT 'Free',
                expiry_date TEXT,
                created_at TEXT
            )
        ''')
        
        # 2. Check for missing columns (Migration for existing DBs)
        c.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'plan_type' not in columns:
            print("Migrating DB: Adding plan_type column...")
            c.execute("ALTER TABLE users ADD COLUMN plan_type TEXT DEFAULT 'Free'")
            
        if 'expiry_date' not in columns:
            print("Migrating DB: Adding expiry_date column...")
            c.execute("ALTER TABLE users ADD COLUMN expiry_date TEXT")

        if 'api_key_hash' not in columns:
            print("Migrating DB: Adding api_key_hash column...")
            c.execute("ALTER TABLE users ADD COLUMN api_key_hash TEXT")
            
        # 3. Create usage limits table
        c.execute('''
            CREATE TABLE IF NOT EXISTS usage_limits (
                email TEXT,
                date TEXT,
                images_count INTEGER DEFAULT 0,
                videos_count INTEGER DEFAULT 0,
                PRIMARY KEY (email, date)
            )
        ''')
        conn.commit()
        conn.close()
        # conn.commit() and conn.close() are handled above
        print(f"[OK] Local SQLite database '{DB_NAME}' initialized/checked.")
    except Exception as e:
        print(f"[FAIL] Database initialization failed: {e}")

def create_user(email, password, full_name, avatar_url=""):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Check if exists
        c.execute("SELECT id FROM users WHERE email = ?", (email,))
        if c.fetchone():
            conn.close()
            return None, "User already exists"
        
        user_id = str(uuid.uuid4())
        hashed_pw = generate_password_hash(password)
        created_at = datetime.now().isoformat()
        
        c.execute("INSERT INTO users (id, email, password_hash, full_name, avatar_url, plan_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (user_id, email, hashed_pw, full_name, avatar_url, 'Free', created_at))
        
        conn.commit()
        conn.close()
        
        return {"id": user_id, "email": email, "full_name": full_name, "avatar_url": avatar_url, "plan_type": "Free"}, None
    except Exception as e:
        return None, str(e)

def get_or_create_google_user(email, full_name, avatar_url=""):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Check if exists
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_row = c.fetchone()
        
        if user_row:
            user = dict(user_row)
            # Update info if changed
            if user['full_name'] != full_name or user['avatar_url'] != avatar_url:
                c.execute("UPDATE users SET full_name = ?, avatar_url = ? WHERE email = ?", (full_name, avatar_url, email))
                conn.commit()
                user['full_name'] = full_name
                user['avatar_url'] = avatar_url
            conn.close()
            return user, None
        
        user_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()
        
        # password_hash is None for Google users
        c.execute("INSERT INTO users (id, email, password_hash, full_name, avatar_url, plan_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                  (user_id, email, None, full_name, avatar_url, 'Free', created_at))
        
        conn.commit()
        conn.close()
        
        return {"id": user_id, "email": email, "full_name": full_name, "avatar_url": avatar_url, "plan_type": "Free"}, None
    except Exception as e:
        return None, str(e)

def get_user_by_email(email):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        conn.close()
        return dict(user) if user else None
    except:
        return None

def upgrade_user_to_pro(email, plan_type='Pro', days=30):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        expiry_date = (datetime.now() + timedelta(days=days)).isoformat()
        c.execute("UPDATE users SET plan_type = ?, expiry_date = ? WHERE email = ?", (plan_type, expiry_date, email))
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def authenticate_user(email, password):
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        user_row = c.fetchone()
        conn.close()
        
        if not user_row:
            return None, "User not found"
            
        if not check_password_hash(user_row['password_hash'], password):
            return None, "Invalid password"
            
        return dict(user_row), None
    except Exception as e:
        print(f"Auth DB Error: {e}")
        return None, str(e)

def update_user_profile(user_id, updates):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        fields = []
        values = []
        for k, v in updates.items():
            if k in ['full_name', 'avatar_url']:
                fields.append(f"{k} = ?")
                values.append(v)
        
        if not fields:
            conn.close()
            return False, "No valid fields"
            
        values.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
        
        c.execute(query, tuple(values))
        rows_affected = c.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected == 0:
            return False, "User not found or no changes made"
            
        return True, None
    except Exception as e:
        return False, str(e)

def get_usage(email):
    """Returns (images_count, videos_count) for the current date."""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT images_count, videos_count FROM usage_limits WHERE email = ? AND date = ?", (email, today))
        row = c.fetchone()
        conn.close()
        if row:
            return row[0], row[1]
        return 0, 0
    except Exception as e:
        print(f"Usage DB Error: {e}")
        return 0, 0

def increment_usage(email, usage_type):
    """Increments image or video usage count for today."""
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Ensure record exists for today
        c.execute("INSERT OR IGNORE INTO usage_limits (email, date) VALUES (?, ?)", (email, today))
        
        if usage_type == 'image':
            c.execute("UPDATE usage_limits SET images_count = images_count + 1 WHERE email = ? AND date = ?", (email, today))
        elif usage_type == 'video':
            c.execute("UPDATE usage_limits SET videos_count = videos_count + 1 WHERE email = ? AND date = ?", (email, today))
            
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Increment Usage Error: {e}")
        return False

def save_api_key_for_user(email, key_hash):
    """Save API key hash for a specific user"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE users SET api_key_hash = ? WHERE email = ?", (key_hash, email))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Save API Key Error: {e}")
        return False

def verify_user_api_key(key_hash):
    """Check if an API key hash exists in the DB"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT email, plan_type FROM users WHERE api_key_hash = ?", (key_hash,))
        row = c.fetchone()
        conn.close()
        if row:
            return {"email": row[0], "plan_type": row[1]}
        return None
    except Exception as e:
        print(f"Verify API Key Error: {e}")
        return None

def check_api_key_status(email):
    """Check if a user already has an API key generated"""
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT api_key_hash FROM users WHERE email = ? AND api_key_hash IS NOT NULL", (email,))
        row = c.fetchone()
        conn.close()
        return bool(row)
    except Exception as e:
        print(f"Check API Key Status Error: {e}")
        return False
