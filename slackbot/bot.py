import logging
import slackclient

from aioslacker import Slacker

from aiohttp.web_response import Response

log = logging.getLogger('application')


class SlackManager(object):
    def __init__(self, token):
        self.token = token

    async def send(self, channel, text=None, username=None, as_user=None,
                   parse=None, link_names=None, attachments=None,
                   unfurl_links=None, unfurl_media=None, icon_url=None,
                   icon_emoji=None):
        async with Slacker(token=self.token) as slacker_client:
            res = await slacker_client.chat.post_message(channel, text, username, as_user,
                                                         parse, link_names, attachments,
                                                         unfurl_links, unfurl_media, icon_url,
                                                         icon_emoji)
            """:type: slacker.Response"""
            if not res.successful:
                return res.error

    async def create_dm_id(self, slack_user_id):
        async with Slacker(token=self.token) as slacker_client:
            res = await slacker_client.im.open(user=slack_user_id)
            """:type: slacker.Response"""
            if not res.successful:
                log.error(f'Error creating IM id for user: {slack_user_id}. Error: {res.error}.')
                raise Exception(f'Error creating IM id for user: {slack_user_id}. Error: {res.error}.')
            return res.body['channel']['id']


class SlackBot:

    slack_client = None

    @classmethod
    def init(cls, token):
        log.info('Initializing slack bot with token')
        try:
            cls.slack_client = slackclient.SlackClient(token=token)
            log.info('Successfully initialized slack bot with token')
        except Exception as e:
            log.error('Error initializing slack bot with token. Error: %s', e)
            raise e

    @classmethod
    def create_dm_id(cls, user):
        log.info('Trying to create new DM for slack_user_id: %s', user.slack_id)
        res = cls.slack_client.api_call('conversations.open', users=user.slack_id)
        if not res['ok']:
            log.error('Error creating DM for slack_user_id: %s', user.slack_id)
            raise Exception(f'Error creating DM for slack_user_id: {user.slack_id}. Error: {res["error"]}')
        else:
            dm_id = res['channel']['id']
            return dm_id

    @classmethod
    def get_users(cls):
        pass
        # pprint.pprint(cls.slack_client.api_call('users.list'))
        # self.slack_client.api_call('')

    @classmethod
    def send_notification(cls, **message):
        log.info('Trying to send notification msg: %s', message)
        res = cls.slack_client.api_call('chat.postMessage', **message)
        if not res['ok']:
            log.error('Error sending notification. %s. Error: %s', message, res['error'])
        else:
            log.info('Successfully sent notification. %s', message)

    @classmethod
    def reportable(cls, fn):
        async def wrapped(*args, **kwargs):
            try:
                return await fn(*args, **kwargs)
            except Exception as e:

                data = {
                    'channel': 'D9RRYLUES',  # todo make this dynamic
                    'text': 'Error occurred :{',
                    'attachments': [
                        {
                            'fallback': f'{e}',
                            'text': f'{e}',
                            'color': '#F35A00'
                        }
                    ]
                }
                cls.send_notification(**data)
                return Response(body=None)

        return wrapped
