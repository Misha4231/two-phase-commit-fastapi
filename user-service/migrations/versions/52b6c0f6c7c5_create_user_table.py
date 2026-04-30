"""create user table

Revision ID: 52b6c0f6c7c5
Revises:
Create Date: 2026-04-29 10:30:41.679846

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "52b6c0f6c7c5"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True, index=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("balance", sa.Integer, default=0),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
