import sqlalchemy as sa

from ..engine import meta


User = sa.Table(
    'users', meta,

    sa.Column('id', sa.Integer),
    sa.Column('slack_id', sa.CHAR(32), unique=True),
    sa.Column('slack_username', sa.CHAR(100), default=None),
    sa.Column('slack_dm_id', sa.CHAR(32), unique=True),
    sa.Column('github_username', sa.CHAR(100), default=None, unique=True),
    sa.Column('github_email', sa.CHAR(100), default=None),

    sa.PrimaryKeyConstraint('id', name='users_id')
)
