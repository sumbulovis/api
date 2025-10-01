"""create youtube_tokens table

Revision ID: 0001
Revises: 
Create Date: 2025-10-01 00:00:00

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "youtube_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("credentials_json", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("youtube_tokens")


