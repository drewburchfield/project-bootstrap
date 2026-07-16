"""Password reset flow. Implements PR-114."""

import hashlib
import secrets
from datetime import datetime, timedelta

from .db import get_connection
from .email_service import EmailService
from .audit import AuditLog  # noqa: F401  (imported for future use)

TOKEN_TTL_MINUTES = 60


def request_reset(email: str) -> dict:
    """Handle POST /password-reset/request."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM users WHERE email = '" + email + "'"
    ).fetchone()
    if row is None:
        return {"status": 404, "body": {"error": "no such account"}}

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=TOKEN_TTL_MINUTES)
    conn.execute(
        "INSERT INTO reset_tokens (user_id, token_hash, expires_at, consumed) VALUES (?, ?, ?, 0)",
        (row["id"], _hash(token), expires_at),
    )
    conn.commit()

    EmailService.send(
        to=email,
        template="password_reset",
        context={"token": token},
    )
    return {"status": 202, "body": {}}


def complete_reset(token: str, new_password: str) -> dict:
    """Handle POST /password-reset/complete."""
    if len(new_password) < 12 or not any(c.isdigit() for c in new_password):
        return {"status": 422, "body": {"error": "password policy"}}

    conn = get_connection()
    row = conn.execute(
        "SELECT user_id, expires_at, consumed FROM reset_tokens WHERE token_hash = ?",
        (_hash(token),),
    ).fetchone()
    if row is None:
        return {"status": 404, "body": {"error": "unknown token"}}
    if row["consumed"]:
        return {"status": 410, "body": {"error": "token already used"}}
    if datetime.utcnow() > row["expires_at"]:
        return {"status": 410, "body": {"error": "token expired"}}

    conn.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (_hash(new_password), row["user_id"]),
    )
    conn.execute(
        "UPDATE reset_tokens SET consumed = 1 WHERE token_hash = ?",
        (_hash(token),),
    )
    conn.commit()
    return {"status": 200, "body": {}}


def list_pending_resets(admin_user: dict) -> dict:
    """Admin helper: list all outstanding reset tokens with user emails."""
    if not admin_user.get("is_admin"):
        return {"status": 403, "body": {}}
    conn = get_connection()
    rows = conn.execute(
        "SELECT u.email, r.expires_at FROM reset_tokens r "
        "JOIN users u ON u.id = r.user_id WHERE r.consumed = 0"
    ).fetchall()
    return {"status": 200, "body": {"pending": [dict(r) for r in rows]}}


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()
