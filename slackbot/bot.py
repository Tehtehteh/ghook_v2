import pprint
import logging
import slackclient

from database import Session

log = logging.getLogger('application')


class SlackBot:

    slack_client = None

    @classmethod
    def init(cls, token):
        log.info('Initializing slack bot with token')
        try:
            cls.slack_client = slackclient.SlackClient(token=token)
            log.info('Successfully initialized slack bot with token')
        except Exception as e:
            log.error('Error initializing slack bot with token')
            raise e

    @classmethod
    def create_dm_id(cls, user):
        log.info('Trying to create new DM for slack_user_id: %i', user.slack_id)
        res = cls.slack_client.api_call('conversations.open', users=user.slack_id)
        if not res['ok']:
            log.error('Error creating DM for slack_user_id: %i', user.slack_id)
            raise Exception(f'Error creating DM for slack_user_id: {user.slack_id}')
        else:
            dm_id = res['channel']['id']
            return dm_id

    @classmethod
    def get_users(cls):
        pprint.pprint(cls.slack_client.api_call('users.list'))
        # self.slack_client.api_call('')

    @classmethod
    def send_notification(cls, dm_id, message):
        log.info('Trying to send notification to %i, msg: %s', dm_id, message)
        data = {
            'channel': dm_id,
            'text': message,
            'as_user': False
        }
        res = cls.slack_client.api_call('chat.postMessage', **data)
        if not res['ok']:
            log.error('Error sending notification to %i', dm_id)
        else:
            log.info('Successfully sent notification to %i', dm_id)
