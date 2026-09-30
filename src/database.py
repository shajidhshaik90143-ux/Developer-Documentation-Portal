import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "docs.db"
DATA_DIR.mkdir(exist_ok=True)

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT NOT NULL UNIQUE,
            summary TEXT DEFAULT '',
            content TEXT DEFAULT '',
            category TEXT DEFAULT 'General',
            tags TEXT DEFAULT '',
            author TEXT DEFAULT 'Admin',
            status TEXT DEFAULT 'Draft',
            difficulty TEXT DEFAULT 'Beginner',
            views INTEGER DEFAULT 0,
            favorite INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT DEFAULT '',
            created_at TEXT NOT NULL,
            FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS api_endpoints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            method TEXT NOT NULL,
            path TEXT NOT NULL,
            category TEXT DEFAULT 'General',
            description TEXT DEFAULT '',
            parameters TEXT DEFAULT '',
            response TEXT DEFAULT '',
            auth TEXT DEFAULT 'None',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            language TEXT NOT NULL,
            code TEXT NOT NULL,
            description TEXT DEFAULT '',
            tags TEXT DEFAULT '',
            created_at TEXT NOT NULL
        );
        """)

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def create_document(data):
    timestamp = now()
    with get_connection() as conn:
        cur = conn.execute("""
            INSERT INTO documents
            (title, slug, summary, content, category, tags, author, status, difficulty, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["title"], data["slug"], data.get("summary",""), data.get("content",""),
            data.get("category","General"), data.get("tags",""), data.get("author","Admin"),
            data.get("status","Draft"), data.get("difficulty","Beginner"), timestamp, timestamp
        ))
        doc_id = cur.lastrowid
        conn.execute(
            "INSERT INTO versions(document_id,title,content,created_at) VALUES(?,?,?,?)",
            (doc_id, data["title"], data.get("content",""), timestamp)
        )
        return doc_id

def update_document(doc_id, data):
    timestamp = now()
    with get_connection() as conn:
        old = conn.execute("SELECT title, content FROM documents WHERE id=?", (doc_id,)).fetchone()
        conn.execute("""
            UPDATE documents SET title=?, slug=?, summary=?, content=?, category=?, tags=?,
            author=?, status=?, difficulty=?, updated_at=? WHERE id=?
        """, (
            data["title"], data["slug"], data.get("summary",""), data.get("content",""),
            data.get("category","General"), data.get("tags",""), data.get("author","Admin"),
            data.get("status","Draft"), data.get("difficulty","Beginner"), timestamp, doc_id
        ))
        if old and (old["title"] != data["title"] or old["content"] != data.get("content","")):
            conn.execute(
                "INSERT INTO versions(document_id,title,content,created_at) VALUES(?,?,?,?)",
                (doc_id, data["title"], data.get("content",""), timestamp)
            )

def delete_document(doc_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM documents WHERE id=?", (doc_id,))

def get_documents():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM documents ORDER BY updated_at DESC").fetchall()

def get_document(doc_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()

def increment_views(doc_id):
    with get_connection() as conn:
        conn.execute("UPDATE documents SET views=views+1 WHERE id=?", (doc_id,))

def toggle_favorite(doc_id):
    with get_connection() as conn:
        conn.execute("UPDATE documents SET favorite=CASE WHEN favorite=1 THEN 0 ELSE 1 END WHERE id=?", (doc_id,))

def get_versions(doc_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM versions WHERE document_id=? ORDER BY created_at DESC", (doc_id,)
        ).fetchall()

def create_api(data):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO api_endpoints
            (name, method, path, category, description, parameters, response, auth, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["name"], data["method"], data["path"], data.get("category","General"),
            data.get("description",""), data.get("parameters",""), data.get("response",""),
            data.get("auth","None"), now()
        ))

def get_apis():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM api_endpoints ORDER BY created_at DESC").fetchall()

def delete_api(api_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM api_endpoints WHERE id=?", (api_id,))

def create_snippet(data):
    with get_connection() as conn:
        conn.execute("""
            INSERT INTO snippets(title,language,code,description,tags,created_at)
            VALUES(?,?,?,?,?,?)
        """, (
            data["title"], data["language"], data["code"], data.get("description",""),
            data.get("tags",""), now()
        ))

def get_snippets():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM snippets ORDER BY created_at DESC").fetchall()

def delete_snippet(snippet_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM snippets WHERE id=?", (snippet_id,))

def search_documents(query):
    q = f"%{query}%"
    with get_connection() as conn:
        return conn.execute("""
            SELECT * FROM documents
            WHERE title LIKE ? OR summary LIKE ? OR content LIKE ?
               OR category LIKE ? OR tags LIKE ? OR author LIKE ?
            ORDER BY updated_at DESC
        """, (q,q,q,q,q,q)).fetchall()

def stats():
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) c FROM documents").fetchone()["c"]
        published = conn.execute("SELECT COUNT(*) c FROM documents WHERE status='Published'").fetchone()["c"]
        drafts = conn.execute("SELECT COUNT(*) c FROM documents WHERE status='Draft'").fetchone()["c"]
        archived = conn.execute("SELECT COUNT(*) c FROM documents WHERE status='Archived'").fetchone()["c"]
        views = conn.execute("SELECT COALESCE(SUM(views),0) c FROM documents").fetchone()["c"]
        favorites = conn.execute("SELECT COUNT(*) c FROM documents WHERE favorite=1").fetchone()["c"]
        apis = conn.execute("SELECT COUNT(*) c FROM api_endpoints").fetchone()["c"]
        snippets = conn.execute("SELECT COUNT(*) c FROM snippets").fetchone()["c"]
        return dict(total=total, published=published, drafts=drafts, archived=archived,
                    views=views, favorites=favorites, apis=apis, snippets=snippets)
