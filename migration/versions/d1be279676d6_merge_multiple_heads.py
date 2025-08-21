"""merge multiple heads

Revision ID: d1be279676d6
Revises: 08bdc7c639ba, cd447afc3a0a
Create Date: 2025-08-18 02:01:07.560582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1be279676d6'
down_revision: Union[str, Sequence[str], None] = ('08bdc7c639ba', 'cd447afc3a0a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
