"""add audit timestamp columns

Revision ID: 3ae937608294
Revises: 0e5e9e4a570d
Create Date: 2026-01-16 20:40:57.197205

"""

from datetime import datetime
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3ae937608294"
down_revision: Union[str, Sequence[str], None] = "0e5e9e4a570d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("weather") as batch_op:
        batch_op.add_column(
            sa.Column(
                "created_at",
                sa.DateTime,
                default=datetime.now,
                server_default=sa.func.now(),
            )
        )
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime,
                default=datetime.now,
                server_default=sa.func.now(),
                server_onupdate=sa.FetchedValue(),
            )
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("weather") as batch_op:
        batch_op.drop_column("created_at")
        batch_op.drop_column("updated_at")
