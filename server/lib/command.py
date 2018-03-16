import logging
import urllib

from urllib import parse

import requests

from database import Session, User
from server.pipeline import Pipelined
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

    @Pipelined(['add_poop'])
    def signin(self):
        """

        :return: response text (either error or an successful answer)
        """
        self.payload = parse.parse_qs(self.payload)
        Session.flush(User)
        Session.commit()
        user_id = self.payload.get('user_id')
        if not user_id:
            log.error('User id is not present in payload @ signin action')
            return
        github_username = self.payload.get('text')
        if isinstance(github_username, list) and len(github_username) == 1:
            github_username, = github_username
            slack_username = self.payload.get('user_name').pop()
            log.info('Verifying user %s and it\'s github username %s', slack_username, github_username)

            url = f'https://api.github.com/users/{github_username}'
            res = requests.get(url)
            if res.status_code == 404:  # todo back in slack with error
                log.error('Github user %s not found.', github_username)
                return f'No such github user: {github_username}.'
            user_slack_id = self.payload.get('user_id')
            if isinstance(user_slack_id, list) and len(user_slack_id) == 1:
                user_slack_id, = user_slack_id
            else:
                log.error('Error parsing slack user id with payload: %s', self.payload)
                return "Error parsing your slack user id -_-"
            user = Session.query(User.slack_id).filter_by(slack_id=user_slack_id).first()
            if user:
                log.warning('User %s is already registered in database with github username %s',
                            user.slack_id, github_username)
                return f'You have been already registered with this github username: {github_username}'
            log.info('Registering new user in our database')
            user = User(github_username=github_username, slack_id=user_slack_id, slack_username=slack_username)
            log.info('Successfully registered new user %r', user)
            Session.add(user)
            Session.commit()
            return f'Successfully registered you as {github_username}.'
        else:
            log.error('Error parsing github username')
            return f'Error parsing {self.payload.get("text")}'

    @Pipelined(['append_poop'])
    def review_requested(self):
        """
        Function which handles review_requested action from GitHub API.
        :return: dm_id, msg for SlackApi
        """
        Session.flush()
        pull_request_url = self.payload['pull_request']['html_url']
        reviewer, = self.payload['pull_request']['requested_reviewers']
        github_username = reviewer['login']
        if not Session.is_active:
            log.warning('Fucking database...')
            Session.refresh()
        user = Session.query(User).filter_by(github_username=github_username).one()  # todo check if user is subscribed
        dm_id = user.slack_dm_id
        if not user:
            log.warning('Couldn\'t find user in our database with this github email: %s', github_username)
        text = f'<@{user.slack_id}>, please check PR: {pull_request_url}'
        if not dm_id:
            dm_id = SlackBot.create_dm_id(user)
            user.slack_dm_id = dm_id
            Session.commit()
            log.info('Successfully set new dm id for user %s', User)
        msg = {
            'dm_id': dm_id,
            'text': text,
            'as_user': False  # todo Variable?
        }
        return msg
