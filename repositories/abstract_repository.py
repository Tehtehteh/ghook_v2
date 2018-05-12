import logging

from abc import ABC

import sqlalchemy as sa

from .history import History

log = logging.getLogger('application')


class AbstractRepository(ABC):

    def __init__(self, tbl):
        self.tbl = tbl
        self.history = History()

    def build_whereclause_from_kwargs(self, **kwargs):
        if self.validate_kwargs_against_table(**kwargs):
            return sa.and_(*[self.tbl.c[kwarg] == kwargs[kwarg] for kwarg in kwargs])
        else:
            self.history.add_failed()
            log.error('Columns in where clause are missing in target table.')
            raise Exception(f'Columns in where clause are missing in target table. {kwargs}')

    @staticmethod
    def get_cache_key_from_kwargs(prefix, **kwargs):
        key = ",".join([f'{k}:{v}' for k, v in kwargs.items()])
        key = f'{prefix}:({key})'
        return key

    def validate_kwargs_against_table(self, **kwargs):
        return all([x in self.tbl.c for x in kwargs])
