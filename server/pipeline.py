import logging

log = logging.getLogger('application')


class Pipeline:

    @classmethod
    def add_poop(cls, msg):
        if 'text' in msg:
            msg += ':poop:'
        elif isinstance(msg, str):
            msg += ' :poop:'
        return msg


class Pipelined:
    def __init__(self, pipelines):
        self.pipelines = pipelines

    def __call__(self, func):
        def wrapped(*args, **kwargs):
            msg = func(*args, **kwargs)
            if self.pipelines:
                for pipeline in self.pipelines:
                    pipelined_func = getattr(Pipeline, pipeline)
                    if callable(pipelined_func):
                        msg = pipelined_func(msg)
            return msg
        return wrapped
