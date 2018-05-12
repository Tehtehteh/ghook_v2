import sqlalchemy as sa

from .domains import RepoType

from ..engine import meta


repository_t = sa.Table(
    'repositories', meta,
    sa.Column('subscribed_user_id', None, sa.ForeignKey('users.id')),
    sa.Column('repo_url', sa.CHAR(100)),
    # sa.Column('repo_url', sa.CHAR(100), sa.Constraint('repo_url LIKE \'https://github.com%\'',
    #                                                   name='repo_url_constraint')),
    sa.Column('repo_type', sa.Enum(RepoType), default=RepoType.github),
    sa.PrimaryKeyConstraint('subscribed_user_id', 'repo_url', 'repo_type', name='repositories_pk')
)
