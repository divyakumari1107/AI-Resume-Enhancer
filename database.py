import sqlite3
import json
from datetime import datetime
from config import Config


def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the SQLite database schema if tables do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table: Resumes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        raw_text TEXT NOT NULL,
        parsed_data TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table: Analyses (ATS Scoring & Job Matching History)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        target_role TEXT,
        job_description TEXT,
        ats_score INTEGER NOT NULL,
        improved_score INTEGER,
        match_percentage INTEGER DEFAULT 0,
        section_scores TEXT,
        matched_keywords TEXT,
        missing_keywords TEXT,
        suggestions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    );
    """)

    # Table: AI Enhancements (Before and After records)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS enhancements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        resume_id INTEGER,
        section_type TEXT NOT NULL,
        original_text TEXT NOT NULL,
        enhanced_text TEXT NOT NULL,
        improvements TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (resume_id) REFERENCES resumes (id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()


def save_resume(filename, original_filename, file_type, file_size, raw_text, parsed_data=None):
    """Save an uploaded resume and its extracted data."""
    conn = get_db_connection()
    cursor = conn.cursor()
    parsed_json = json.dumps(parsed_data) if parsed_data else None

    cursor.execute("""
        INSERT INTO resumes (filename, original_filename, file_type, file_size, raw_text, parsed_data)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (filename, original_filename, file_type, file_size, raw_text, parsed_json))

    resume_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return resume_id


def get_resume(resume_id):
    """Retrieve a single resume by its ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    resume = dict(row)
    if resume.get("parsed_data"):
        try:
            resume["parsed_data"] = json.loads(resume["parsed_data"])
        except Exception:
            resume["parsed_data"] = {}
    else:
        resume["parsed_data"] = {}
    return resume


def update_resume_parsed_data(resume_id, parsed_data):
    """Update parsed data for an existing resume."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE resumes
        SET parsed_data = ?
        WHERE id = ?
    """, (json.dumps(parsed_data), resume_id))
    conn.commit()
    conn.close()


def get_all_resumes(limit=50):
    """Retrieve all resumes, ordered by newest first."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()

    resumes = []
    for row in rows:
        item = dict(row)
        if item.get("parsed_data"):
            try:
                item["parsed_data"] = json.loads(item["parsed_data"])
            except Exception:
                item["parsed_data"] = {}
        resumes.append(item)
    return resumes


def save_analysis(resume_id, ats_score, improved_score=None, match_percentage=0,
                  target_role="", job_description="", section_scores=None,
                  matched_keywords=None, missing_keywords=None, suggestions=None):
    """Save an ATS analysis and job matching result."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO analyses (
            resume_id, target_role, job_description, ats_score,
            improved_score, match_percentage, section_scores,
            matched_keywords, missing_keywords, suggestions
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        resume_id,
        target_role,
        job_description,
        ats_score,
        improved_score or min(100, ats_score + 18),
        match_percentage,
        json.dumps(section_scores or {}),
        json.dumps(matched_keywords or []),
        json.dumps(missing_keywords or []),
        json.dumps(suggestions or [])
    ))

    analysis_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return analysis_id


def get_analysis(analysis_id):
    """Fetch an analysis record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, r.original_filename, r.file_type
        FROM analyses a
        LEFT JOIN resumes r ON a.resume_id = r.id
        WHERE a.id = ?
    """, (analysis_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    analysis = dict(row)
    for field in ["section_scores", "matched_keywords", "missing_keywords", "suggestions"]:
        if analysis.get(field):
            try:
                analysis[field] = json.loads(analysis[field])
            except Exception:
                analysis[field] = {} if "scores" in field else []
    return analysis


def get_all_analyses(limit=50):
    """Retrieve full history of analyses."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, r.original_filename, r.file_type
        FROM analyses a
        LEFT JOIN resumes r ON a.resume_id = r.id
        ORDER BY a.created_at DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    analyses = []
    for row in rows:
        item = dict(row)
        for field in ["section_scores", "matched_keywords", "missing_keywords", "suggestions"]:
            if item.get(field):
                try:
                    item[field] = json.loads(item[field])
                except Exception:
                    item[field] = {} if "scores" in field else []
        analyses.append(item)
    return analyses


def delete_analysis(analysis_id):
    """Delete an analysis record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def clear_all_analyses():
    """Clear all analysis history records."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM analyses")
    conn.commit()
    conn.close()


def save_enhancement(resume_id, section_type, original_text, enhanced_text, improvements=None):
    """Record an AI enhancement comparison."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO enhancements (resume_id, section_type, original_text, enhanced_text, improvements)
        VALUES (?, ?, ?, ?, ?)
    """, (
        resume_id,
        section_type,
        original_text,
        enhanced_text,
        json.dumps(improvements or [])
    ))
    enhancement_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return enhancement_id


def get_enhancements_by_resume(resume_id):
    """Fetch enhancements for a specific resume."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM enhancements
        WHERE resume_id = ?
        ORDER BY created_at DESC
    """, (resume_id,))
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        item = dict(row)
        if item.get("improvements"):
            try:
                item["improvements"] = json.loads(item["improvements"])
            except Exception:
                item["improvements"] = []
        results.append(item)
    return results


def get_dashboard_stats():
    """Compute aggregate dashboard metrics from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM resumes")
    total_resumes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*), AVG(ats_score), AVG(match_percentage) FROM analyses")
    row = cursor.fetchone()
    total_analyses = row[0] or 0
    avg_ats = round(row[1], 1) if row[1] is not None else 0
    avg_match = round(row[2], 1) if row[2] is not None else 0

    cursor.execute("SELECT COUNT(*) FROM enhancements")
    total_enhancements = cursor.fetchone()[0]

    # Recent activity
    cursor.execute("""
        SELECT a.id, a.ats_score, a.match_percentage, a.target_role, a.created_at,
               r.original_filename, r.id as resume_id
        FROM analyses a
        LEFT JOIN resumes r ON a.resume_id = r.id
        ORDER BY a.created_at DESC
        LIMIT 5
    """)
    recent_activity = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "total_resumes": total_resumes,
        "total_analyses": total_analyses,
        "avg_ats": avg_ats,
        "avg_match": avg_match,
        "total_enhancements": total_enhancements,
        "recent_activity": recent_activity
    }
