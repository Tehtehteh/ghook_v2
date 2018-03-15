import logging

from database import User, Session
from slackbot.bot import SlackBot


log = logging.getLogger('application')


class Pipeline:

    @classmethod
    def build_message(cls, pull_request_url, github_username):
        if not Session.is_active:
            log.warning('Fucking database...')
            Session.refresh()
        query = Session.query(User).filter_by(github_username=github_username)
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

