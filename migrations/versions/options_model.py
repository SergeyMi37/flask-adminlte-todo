"""Create options model for user settings"""

import datetime
from alembic import op
import sqlalchemy as sa


revision = 'options_model'
down_revision = None
branch_label = None
depends_on = None


def upgrade():
    op.create_table(
        'options',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('value', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('options')