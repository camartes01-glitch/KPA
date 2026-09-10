"""add_google_sub_and_nullable_phone

Revision ID: 3bb49ee7ee19
Revises: 
Create Date: 2026-09-10 11:18:34.726161+05:30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3bb49ee7ee19'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('google_sub', sa.String(length=255), nullable=True))
        batch_op.alter_column('phone',
                   existing_type=sa.VARCHAR(length=20),
                   nullable=True)
        batch_op.create_index('ix_users_google_sub', ['google_sub'], unique=True)


def downgrade() -> None:
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index('ix_users_google_sub')
        batch_op.alter_column('phone',
                   existing_type=sa.VARCHAR(length=20),
                   nullable=False)
        batch_op.drop_column('google_sub')
