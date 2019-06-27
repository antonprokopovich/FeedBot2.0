"""create users table

Revision ID: 2acb44526761
Revises: 
Create Date: 2019-05-01 17:34:26.372569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2acb44526761'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('nickname', sa.String(100), nullable=False),
    )


def downgrade():
    op.drop_table('users')
