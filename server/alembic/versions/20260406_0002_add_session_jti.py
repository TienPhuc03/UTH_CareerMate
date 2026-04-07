"""align auth migration history

Revision ID: 20260406_0002
Revises: 9e6bf53036ad
Create Date: 2026-04-06 12:00:00.000000
"""

revision = "20260406_0002"
down_revision = "9e6bf53036ad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The session-jti schema change was dropped from the application code.
    # Keep this revision as a no-op so existing revision ids remain valid
    # while Alembic has a single linear history.
    return None


def downgrade() -> None:
    return None
