# Feature Spec: Password Reset Flow (PR-114)

Originating ticket: PR-114 "Self-serve password reset"

## Requirements

- **R1 — Request endpoint.** `POST /password-reset/request` accepts `{email}`. It MUST always return `202 Accepted` regardless of whether the email matches an account, to prevent user enumeration.
- **R2 — Token expiry.** Reset tokens MUST expire 30 minutes after issuance.
- **R3 — Single use.** A reset token MUST be invalidated after one successful password reset. Reusing a consumed token returns `410 Gone`.
- **R4 — Password policy.** New passwords MUST be at least 12 characters and contain at least one digit.
- **R5 — Rate limiting.** At most 3 reset requests per email address per rolling hour. Excess requests still return `202` but MUST NOT send email or mint tokens.
- **R6 — Notification and audit.** On request, send the reset email via `EmailService`. On successful reset completion, emit an audit event via `AuditLog.record("password_reset_completed", user_id)`.

## Out of scope

Nothing beyond the above. No admin tooling, no UI, no SMS channel.
