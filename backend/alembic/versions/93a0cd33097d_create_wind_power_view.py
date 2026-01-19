"""create wind power view

Revision ID: 93a0cd33097d
Revises: 3ae937608294
Create Date: 2026-01-19 22:22:18.220593

"""
from typing import Sequence, Union
from pathlib import Path

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93a0cd33097d'
down_revision: Union[str, Sequence[str], None] = '3ae937608294'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_sql_content(filename):
    base_dir = Path(__file__).resolve().parents[2]
    sql_path = base_dir / "src/sql" / filename
    return sql_path.read_text()


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("DROP VIEW IF EXISTS v_wind_power")
    sql = get_sql_content("v_wind_power.sql")
    op.execute(sql)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP VIEW v_wind_power")
