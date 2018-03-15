import logging

from database import Session, User
from slackbot.bot import SlackBot

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
        """
        Function which handles review_requested action from GitHub API.
        :return: dm_id, msg for SlackApi
        """
        pull_request_url = self.payload['pull_request']['html_url']
        reviewer, = self.payload['pull_request']['requested_reviewers']
        github_username = reviewer['login']
        if not Session.is_active:
            log.warning('Fucking database...')
            Session.refresh()
        query = Session.query(User).filter_by(github_username=github_username)  # todo check if user is subscribed
        user = query.first()
        dm_id = user.slack_dm_id
        if not user:
            log.warning('Couldn\'t find user in our database with this github email: %s', github_username)
        msg = f'<@{user.slack_id}>, please check PR: {pull_request_url}'
        if not dm_id:
            dm_id = SlackBot.create_dm_id(user)
            user.slack_dm_id = dm_id
            Session.commit()
            log.info('Successfully set new dm id for user %s', User)
        SlackBot.send_notification(dm_id, msg)
