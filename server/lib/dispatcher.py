import logging

from .command import Command


log = logging.getLogger('Application')


class Dispatcher:

    @classmethod
    def dispatch_action(cls, action, payload):
        log.info('Dispatching %s action.', action)
        return Command(action, payload).do()
