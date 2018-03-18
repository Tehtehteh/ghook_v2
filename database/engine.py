import os

import sqlalchemy as sa


engine = sa.create_engine(os.environ.get('SQLALCHEMY_ENGINE'),
                          pool_recycle=3600,
                          echo_pool=bool(os.environ.get('DEBUG', False)),
                          echo=bool(os.environ.get('DEBUG', False)))

meta = sa.MetaData(bind=engine)
