import logging

from ..pipeline import Pipeline

log = logging.getLogger('application')


class Command:

    def __init__(self, action, payload):
        self.action = action
        self.payload = payload

    def do(self):
        if hasattr(self, self.action) and callable(getattr(self, self.action)):
            log.info('Command found, doing %s.', self.action)
            return getattr(self, self.action)()
        else:
            log.info('Command not found: %s.', self.action)
            return

    def closed(self):
        pass

    def review_requested(self):
        pull_request_url = self.payload['pull_request']['html_url']
        reviewer, = self.payload['pull_request']['requested_reviewers']
        github_username = reviewer['login']
        Pipeline.build_message(pull_request_url, github_username)
