"""Add subs (subscriptions) and channels tables

Revision ID: f5a627fe3037
Revises: 2acb44526761
Create Date: 2019-05-01 19:05:08.345437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f5a627fe3037'
down_revision = '2acb44526761'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'channels',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(500), nullable=False),
    )

    op.create_table(
        'subs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('channel_id', sa.Integer, sa.ForeignKey('channels.id'), nullable=False),
    )


def downgrade():
    op.drop_table('subs')
    op.drop_table('channels')
