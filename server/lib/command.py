import logging

from urllib import parse

import requests
import sqlalchemy as sa

from database import User, Repository
from server.pipeline import Pipelined
from slackbot.bot import SlackBot

from .utils import attach_message

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

    def get_user(self):
        pass

    def get_repo(self):
        pass

    @Pipelined(['add_poop', 'add_poop'])
    def subscribe(self):
        self.payload = parse.parse_qs(self.payload)
        github_repo = self.payload.get('text').pop()
        github_repo = github_repo.rstrip('>').lstrip('<')
        user_slack_id = self.payload.get('user_id').pop()
        user = sa.select([User]).where(User.c.slack_id == user_slack_id).execute().fetchone()
        msg = {
            'text': '',
        }
        if not user:
            return attach_message(msg, 'You must first register via /signin %your_github_username%')
        repo = sa.select([Repository.c.repo_url]).where(sa.and_(Repository.c.subscribed_user_id == user.id,
                                                                Repository.c.repo_url == github_repo.lower())).execute().fetchone()

        if repo:
            return attach_message(msg, f'You are already subscribed to this repository {github_repo}')
        log.info('Subscribing %s to %s', self.payload.get('user_name', []).pop(), github_repo)

        Repository.insert().values({'subscribed_user_id': user.id, 'repo_url': github_repo}).execute()

        return attach_message(msg, f'Successfully subscribed to {github_repo}', color='#47a450')

    def unsubscribe(self):
        self.payload = parse.parse_qs(self.payload)
        github_repo = self.payload.get('text').pop()
        github_repo = github_repo.rstrip('>').lstrip('<')
        user_slack_id = self.payload.get('user_id').pop()
        msg = {
            'text': ''
        }

        user = sa.select([User]).where(User.c.slack_id == user_slack_id).execute().fetchone()

        if not user:
            return attach_message(msg, 'You are not registered here')
        repo = sa.select([Repository]).where(sa.and_(
            Repository.c.subscribed_user_id == user.id,
            Repository.c.repo_url.like(github_repo)
        )).execute().fetchone()

        if not repo:
            return attach_message(msg, f'You are not subscribed to this repository {github_repo}')
        log.info('Unsubscribe %s to %s', self.payload.get('user_name', []).pop(), github_repo)
        Repository.delete().where(sa.and_(
            Repository.c.subscribed_user_id == user.id,
            Repository.c.repo_url == repo.repo_url
        )).execute()
        return attach_message(msg, f'Successfully unsubscribed from {github_repo}', color='#47a450')

    @Pipelined(['add_poop'])
    def signin(self):
        """

        :return: response text (either error or an successful answer)
        """
        self.payload = parse.parse_qs(self.payload)
        user_id = self.payload.get('user_id')
        msg = {
            'text': ''
        }
        if not user_id:
            err = 'User id is not present in payload @ signin action'
            log.error(err)
            return attach_message(msg, err)
        github_username = self.payload.get('text')
        if isinstance(github_username, list) and len(github_username) == 1:
            github_username, = github_username
            slack_username = self.payload.get('user_name').pop()
            log.info('Verifying user %s and it\'s github username %s', slack_username, github_username)

            url = f'https://api.github.com/users/{github_username}'
            res = requests.get(url)
            if res.status_code == 404:  # todo back in slack with error
                log.error('Github user %s not found.', github_username)
                return attach_message(msg, f'No such github user: {github_username}.')
            user_slack_id = self.payload.get('user_id')
            if isinstance(user_slack_id, list) and len(user_slack_id) == 1:
                user_slack_id, = user_slack_id
            else:
                log.error('Error parsing slack user id with payload: %s', self.payload)
                return attach_message(msg, f'Error parsing your slack user id -_-')
            user = sa.select([User]).where(User.c.slack_id == user_slack_id).execute().fetchone()
            if user:
                log.warning('User %s is already registered in database with github username %s',
                            user.slack_id, github_username)
                return attach_message(msg,
                                      f'You have been already registered with this github username: {github_username}')
            log.info('Registering new user in our database')
            User.insert().values(
                {
                    'github_username': github_username.lower(),  # normalize github username...
                    'slack_username': slack_username,
                    'slack_id': user_slack_id
                }
            ).execute()
            log.info('Successfully registered %s as %s', slack_username, github_username)
            return attach_message(msg, f'Successfully registered you as {github_username}.', color='#47a450')
        else:
            log.error('Error parsing github username')
            return attach_message(msg, f'error parsing {self.payload.get("text")}')

    @Pipelined(['add_poop'])
    def review_requested(self):
        """
        Function which handles review_requested action from GitHub API.
        :return: dm_id, msg for SlackApi
        """

        pull_request_url = self.payload['pull_request']['html_url']
        repo_full_url = self.payload['repository']['html_url']
        reviewers = self.payload['pull_request']['requested_reviewers']
        messages = []
        for reviewer in reviewers:
            github_username = reviewer['login']
            user = sa.select([User]).where(User.c.github_username == github_username.lower()).execute().fetchone()

            if not user:
                log.warning('Couldn\'t find user in our database with this github email: %s', github_username)
                continue
            dm_id = user.slack_dm_id

            repo = sa.select([Repository]).where(sa.and_(Repository.c.repo_url == repo_full_url,
                                                         Repository.c.subscribed_user_id == user.id)).execute().fetchone()

            if not repo:
                log.warning('User %s is not subscribed for %s repository', github_username, repo_full_url)
                continue

            text = f'<@{user.slack_id}>, please check PR: {pull_request_url}'
            if not dm_id:
                dm_id = SlackBot.create_dm_id(user)
                User.update().where(User.c.id == user.id).values(slack_dm_id=dm_id).execute()

                log.info('Successfully set new dm id for user %s', User)
            msg = {
                'channel': dm_id,
                'text': text,
                'as_user': False  # todo Variable?
            }
            messages.append(msg)
        return messages
