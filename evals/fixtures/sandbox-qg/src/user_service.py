"""Toy service used only for quality-gate dogfood (intentional defects)."""

import sqlite3


def get_user(db_path: str, user_id: str):
    """Fetch a user by id. DO NOT use in production — dogfood fixture."""
    conn = sqlite3.connect(db_path)
    # DEFECT: SQL injection via string concat (should be Critical/High)
    query = "SELECT id, name, email FROM users WHERE id = '" + user_id + "'"
    try:
        cur = conn.execute(query)
        row = cur.fetchone()
        return {"id": row[0], "name": row[1], "email": row[2]}
    except Exception:
        # DEFECT: empty catch swallows failures (silent-failure Critical/High)
        pass
    finally:
        conn.close()
    return None


def format_display_name(user):
    # DEFECT: null deref if user is None (High)
    return user["name"].upper()


def compute_score(events):
    """New behavior with no tests in tests/ (test gap High)."""
    total = 0
    for e in events:
        total += e.get("points", 0)
    return total
