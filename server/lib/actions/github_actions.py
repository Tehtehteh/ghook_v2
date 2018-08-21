import os
import asyncio
import logging

from repositories import UserRepository, RepoRepository
from slackbot.bot import SlackManager

from ..filters.github_filters import is_user_registered
from ..utils import parse_dtm

log = logging.getLogger('application')


class GithubActionFactory(object):

    @classmethod
    def create_action(cls, request):
        action = cls.get_concrete_action(request)
        return action

    @classmethod
    def get_concrete_action(cls, request):
        if request.get('action') == 'review_requested' and request.get('requested_reviewer'):
            params = {
                'github_username': request['pull_request']['user']['login'],
                'github_avatar': request['pull_request']['user']['avatar_url'] or
                                 request['pull_request']['user']['gravatar_url'],
                'github_username_link': request['pull_request']['user']['html_url'],

                'title': request['pull_request']['title'],
                'pr_url': request['pull_request']['html_url'],


                'reviewer': request['requested_reviewer'],
                'message': request['pull_request']['body'],
                'created_at': request['pull_request']['created_at'],
                'branch_from': request['pull_request']['head']['ref'],
                'branch_to': request['pull_request']['base']['ref'],
                'changed_files': request['pull_request']['changed_files'],
                'additions': request['pull_request']['additions'],
                'deletions': request['pull_request']['deletions'],
                'repo_url': request['repository']['html_url'],
                '_request_origin': request['original_request'],
            }
            return ReviewRequestedAction(**params)
        if request.get('action') == 'submitted':
            params = {
                'author': request['pull_request']['user']['login'],
                'sender': request['review']['user']['login'],
                'sender_avatar_url': request['review']['user']['avatar_url'],
                'sender_url': request['review']['user']['html_url'],
                'message': request['review']['body'],
                'state': request['review']['state'],
                'pull_request_url': request['pull_request']['html_url'],
                'pull_request_title': request['pull_request']['title'],
                'submitted_at': request['review']['submitted_at'],
                'repo_url': request['repository']['html_url'],
                '_request_origin': request['original_request'],
            }
            return SubmitAction(**params)
        if request.get('action') == 'opened':
            params = {
                'github_username': request['pull_request']['user']['login'],
                'github_avatar': request['pull_request']['user']['avatar_url'] or
                                 request['pull_request']['user']['gravatar_url'],
                'github_username_link': request['pull_request']['user']['html_url'],
                'title': request['pull_request']['title'],
                'pr_url': request['pull_request']['html_url'],
                'message': request['pull_request']['body'],
                'created_at': request['pull_request']['created_at'],
                'branch_from': request['pull_request']['head']['ref'],
                'branch_to': request['pull_request']['base']['ref'],
                'changed_files': request['pull_request']['changed_files'],
                'additions': request['pull_request']['additions'],
                'deletions': request['pull_request']['deletions'],
                'repo_url': request['repository']['html_url'],
                '_request_origin': request['original_request'],
            }
            return PullRequestOpenedAction(**params)
        else:
            log.warning('Unknown action! Action: %s', request.get('action'))
            return None


class PullRequestOpenedAction(object):
    def __init__(self, *, github_username, github_avatar, github_username_link,
                 title, pr_url, message, created_at, branch_from,
                 branch_to, changed_files, additions, deletions, repo_url,
                 _request_origin, color='#3ae34f', slack_user_id=None,
                 slack_dm_id=None, force_allowed=False):
        self.github_username = github_username
        self.github_avatar = github_avatar
        self.github_username_link = github_username_link
        self.title = title
        self.pr_url = pr_url
        self.message = message
        self.created_at = created_at
        self.branch_from = branch_from
        self.branch_to = branch_to
        self.changed_files = changed_files
        self.additions = additions
        self.deletions = deletions
        self.attachment_color = color
        self.repo_url = repo_url
        self._request_origin = _request_origin
        self.force_allowed = force_allowed

        self.slack_dm_id = slack_dm_id
        self.slack_user_id = slack_user_id

    async def is_allowed(self):
        # if self.force_allowed:
        #     return True
        if len(self._request_origin.app['constants']['force_ping_ids']):
            force_ping_users = self._request_origin.app['constants']['force_ping_ids']
            force_ping_tasks = []
            for force_ping_user in force_ping_users:
                user = await UserRepository().find_one(slack_dm_id=force_ping_user)
                if not user:
                    continue
                repo = await RepoRepository().find_one(repo_url=self.repo_url,
                                                       subscribed_user_id=user.id)
                if not repo:
                    continue
                force_ping_tasks.append(self._request_origin.app['slack_manager'].send(channel=force_ping_user,
                                                                                       **self.to_slack_message()))
            if len(force_ping_tasks):
                # Messy :0
                await asyncio.gather(*force_ping_tasks)
        return False

    def to_slack_message(self):
        text = f'Please check pull request submitted by {self.github_username}'
        return {
            'text': text,
            'attachments': [
                {
                    'color': '#0366d6',
                    'fields': [
                        {
                            'title': 'From branch',
                            'value': self.branch_from,
                            'short': True
                        },
                        {
                            'title': 'To branch',
                            'value': self.branch_to,
                            'short': True
                        }
                    ],
                },
                {
                    'color': '#ffed63',
                    'title': 'Short info',
                    'fields': [
                        {
                            'title': 'Files changed',
                            'value': self.changed_files,
                            'short': True
                        },
                        {
                            'title': 'Additions',
                            'value': self.additions,
                            'short': True
                        },
                        {
                            'title': 'Deletions',
                            'value': self.deletions,
                            'short': True
                        },
                    ],
                },
                {
                    'color': self.attachment_color,
                    'attachment_type': 'default',
                    'author_name': self.github_username,
                    'author_link': self.github_username_link,
                    'author_icon': self.github_avatar,
                    'title': self.title,
                    'title_link': self.pr_url,
                    'text': self.message,
                    'footer': 'check \'em!',
                    'ts': parse_dtm(self.created_at)
                }
            ]
        }


class ReviewRequestedAction(object):

    _filters = [is_user_registered]

    def __init__(self, *, github_username, github_avatar, github_username_link,
                 title, pr_url, reviewer, message, created_at, branch_from,
                 branch_to, changed_files, additions, deletions, repo_url, color='#3ae34f',
                 slack_user_id=None, slack_dm_id=None, force_allowed=False):
        self.github_username = github_username
        self.github_avatar = github_avatar
        self.github_username_link = github_username_link
        self.reviewer = reviewer
        self.title = title
        self.pr_url = pr_url
        self.message = message
        self.created_at = created_at
        self.branch_from = branch_from
        self.branch_to = branch_to
        self.changed_files = changed_files
        self.additions = additions
        self.deletions = deletions
        self.attachment_color = color
        self.repo_url = repo_url
        self.force_allowed = force_allowed

        self.slack_dm_id = slack_dm_id
        self.slack_user_id = slack_user_id

    def _run_filters(self):
        return all([fn() for fn in self._filters])

    async def is_allowed(self):
        if self.force_allowed:
            return True
        user_repository_instance = UserRepository()
        repo_repository_instance = RepoRepository()
        user = await user_repository_instance.find_one(github_username=self.reviewer['login'])
        if not user:
            log.warning('Couldn\'t find user in our database with this github username: %s', self.reviewer['login'])
            return False
        dm_id = user.slack_dm_id

        repo = await repo_repository_instance.find_one(repo_url=self.repo_url, subscribed_user_id=user.id)

        if not repo:
            log.warning('User %s is not subscribed for %s repository', self.reviewer, self.repo_url)
            return False

        if not dm_id:
            dm_id = await SlackManager(token=os.environ.get('SLACK_TOKEN')).create_dm_id(slack_user_id=user.slack_id)
            await user_repository_instance.update(values={'slack_dm_id': dm_id}, id=user.id)
        self.slack_dm_id = user.slack_dm_id
        self.slack_user_id = user.slack_id
        return True

    def on_task_callback(self, result):
        """
        :param result: concurrent.futures.Future
        :return:
        """
        result = result.result()
        if result and result.error is not None:
            log.error('Failed sending message to %s. Error: %s', self.reviewer['login'], result.error)
            raise Exception(result.error)
        log.info('Successfully sent message to %s.', self.reviewer['login'])

    def to_slack_message(self, to_admin=False):
        text = f'Please check pull request submitted by {self.github_username}'
        if self.slack_user_id and not to_admin:
            text = f'<@{self.slack_user_id}>, please check pull request submitted by {self.github_username}'
        return {
            'text': text,
            'attachments': [
                {
                    'color': '#0366d6',
                    'fields': [
                        {
                            'title': 'From branch',
                            'value': self.branch_from,
                            'short': True
                        },
                        {
                            'title': 'To branch',
                            'value': self.branch_to,
                            'short': True
                        }
                    ],
                },
                {
                    'color': '#ffed63',
                    'title': 'Short info',
                    'fields': [
                        {
                            'title': 'Files changed',
                            'value': self.changed_files,
                            'short': True
                        },
                        {
                            'title': 'Additions',
                            'value': self.additions,
                            'short': True
                        },
                        {
                            'title': 'Deletions',
                            'value': self.deletions,
                            'short': True
                        },
                    ],
                },
                {
                    'color': self.attachment_color,
                    'attachment_type': 'default',
                    'author_name': self.github_username,
                    'author_link': self.github_username_link,
                    'author_icon': self.github_avatar,
                    'title': self.title,
                    'title_link': self.pr_url,
                    'text': self.message,
                    'footer': 'check \'em!',
                    'ts': parse_dtm(self.created_at)
                }
            ]
        }


class SubmitAction(object):

    def __init__(self, author, sender, sender_avatar_url, sender_url, message, state, pull_request_url,
                 pull_request_title, submitted_at, repo_url, color=None, force_allowed=False,
                 slack_user_id=None, slack_dm_id=None):
        self.author = author
        self.submit_action = 'requested changes on' if state == 'changes_requested' else 'approved'
        self.attachment_color = color or '#ff0000' if state == 'changes_requested' else '#34d058'
        self.sender = sender
        self.sender_avatar_url = sender_avatar_url
        self.sender_link = sender_url
        self.message = message
        self.pull_request_url = pull_request_url
        self.pull_request_title = pull_request_title
        self.submitted_at = submitted_at
        self.repo_url = repo_url

        self.force_allowed = force_allowed
        self.slack_dm_id = slack_dm_id
        self.slack_user_id = slack_user_id

    async def is_allowed(self):
        if self.force_allowed:
            return True
        user_repository_instance = UserRepository()
        repo_repository_instance = RepoRepository()
        user = await user_repository_instance.find_one(github_username=self.author)
        if not user:
            log.warning('Couldn\'t find user in our database with this github username: %s', self.author)
            return False
        dm_id = user.slack_dm_id

        repo = await repo_repository_instance.find_one(repo_url=self.repo_url, subscribed_user_id=user.id)

        if not repo:
            log.warning('User %s is not subscribed for %s repository', self.author, self.repo_url)
            return False

        if not dm_id:
            dm_id = await SlackManager(token=os.environ.get('SLACK_TOKEN')).create_dm_id(slack_user_id=user.slack_id)
            await user_repository_instance.update(values={'slack_dm_id': dm_id}, id=user.id)
        self.slack_dm_id = user.slack_dm_id
        self.slack_user_id = user.slack_id
        return True

    def on_task_callback(self, result):
        """
        :param result: concurrent.futures.Future
        :return:
        """
        result = result.result()
        if result and result.error is not None:
            log.error('Failed sending message to %s. Error: %s', self.author, result.error)
            raise Exception(result.error)
        log.info('Successfully sent message to %s.', self.author)

    def to_slack_message(self):
        if not self.slack_dm_id:
            return None
        return {
            'text': f'<@{self.slack_user_id}>, {self.sender} {self.submit_action} your pull request.',
            'attachments': [
                {
                    'color': self.attachment_color,
                    'attachment_type': 'default',
                    'author_name': self.sender,
                    'author_link': self.sender_link,
                    'author_icon': self.sender_avatar_url,
                    'title': self.pull_request_title,
                    'title_link': self.pull_request_url,
                    'text': self.message,
                    'footer': 'check \'em!',
                    'ts': parse_dtm(self.submitted_at)
                }
            ]
        }
