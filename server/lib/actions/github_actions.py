import pytz

from datetime import datetime

from .base_action import BaseAction


class GithubActionFactory(object):

    @classmethod
    def create_action(cls, request):
        action = cls.get_concrete_action(request)
        return action

    @classmethod
    def get_concrete_action(cls, request):
        if request['action'] == 'review_requested':
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
            }
            return ReviewRequestedAction(**params)
        else:
            return None


class ReviewRequestedAction(BaseAction):

    def __init__(self, *, github_username, github_avatar, github_username_link,
                 title, pr_url, reviewer, message, created_at, branch_from,
                 branch_to, changed_files, additions, deletions, color='#3ae34f'):
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

    def to_slack_message(self, user_slack_id):
        # todo danamic user_slack id

        def parse_dtm(x):
            return int(pytz.UTC.localize(datetime.strptime(x, '%Y-%m-%dT%H:%M:%SZ')).timestamp())

        return {
            'text': f'<@U7N50A3NX>, please check pull request submitted by {self.github_username}',
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
