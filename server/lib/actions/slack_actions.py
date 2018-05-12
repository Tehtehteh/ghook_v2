import os
import logging


log = logging.getLogger('application')


class SlackActionFactory(object):

    @classmethod
    def create_action(cls, request):
        action = cls.get_concrete_action(request)
        return action

    @classmethod
    def get_concrete_action(cls, request):
        if request.get('command') == '/gsignin':
            params = {
                'user_id': request['user_id'],
                'response_url': request['response_url'],
                'username': request['user_name'],
                'channel_id': request['channel_id'] if request['channel_name'] == 'directmessage' else None
            }
            return GHSignInAction(**params)
        else:
            raise Exception(f'Unknown slack command. Request: {request}')


class GHSignInAction(object):

    def __init__(self, *, user_id, response_url, username, channel_id):
        self.user_id = user_id
        self.response_url = response_url
        self.username = username
        self.channel_id = channel_id

    def on_task_callback(self, result):
        """
        :param result: concurrent.futures.Future
        :return:
        """
        result = result.result()
        if result and result.error is not None:
            log.error('Failed sending message to %s. Error: %s', self.username, result.error)
            raise Exception(result.error)
        log.info('Successfully sent message to %s.', self.username)

    def to_slack_message(self):

        return {
            "text": f"You can sign in to github by clicking on the button below.",
            "attachments": [
                {
                    "text": "Yes. This button.",
                    "fallback": "Something happened to button :{",
                    "color": "#3AA3E3",
                    "attachment_type": "default",
                    "actions": [
                        {
                            "name": "gsignin_btn",
                            "text": "CLICK MEH",
                            "type": "button",
                            "color": "#21ff13",
                            "url": f'{os.environ.get("APP_URL")}/github/oauth/start?slack_user_name={self.username}'
                        },
                    ]
                }
            ]
        }
