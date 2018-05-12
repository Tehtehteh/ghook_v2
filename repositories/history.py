class History(object):

    def __init__(self):
        self.failed = 0
        self.successful = 0
        self.from_cache = 0

    def add_successful(self):
        self.successful += 1

    def add_failed(self):
        self.failed += 1

    def add_cached(self):
        self.from_cache += 1

    def __str__(self):
        msg = ''
        if self.failed:
            msg = f'WARNING: Failed {self.failed} queries.'
        msg += f'Successful: {self.successful} queries. From cache: {self.from_cache}. '
        return msg
