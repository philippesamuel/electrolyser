"""initial

Revision ID: cf3db07e76cf
Revises:
Create Date: 2026-01-13 15:50:56.002458

"""

from typing import Sequence, Union

from alembic import op

from loguru import logger

# revision identifiers, used by Alembic.
revision: str = "cf3db07e76cf"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with open("alembic/database.sql", "r") as f:
        skip_lines = ("--", "BEGIN TRANSACTION", "COMMIT", "PRAGMA")
        raw_sql_commands = f.read().split(";\n")
        _ = (line.strip() for line in raw_sql_commands)
        sql_commands = (
            line for line in _ if line and not line.startswith(skip_lines)
        )  # remove empty lines
        for command in sql_commands:
            logger.info(f"Executing SQL command: {command}")
            op.execute(command)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE IF EXISTS weather;")
