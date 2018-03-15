import pprint

import slackclient


class SlackBot:

    def __init__(self, token):
        self.slack_client = slackclient.SlackClient(token=token)

    def get_users(self):
        pprint.pprint(self.slack_client.api_call('users.list'))
        # self.slack_client.api_call('')

    def send_notification(self, user_id):
        created = self.slack_client.api_call('conversations.open', users=user_id)
        if created['ok']:
            im_id = created['channel']['id']
            data = {
                'channel': im_id,
                'text': f'<@{user_id}>, Ayoooo, hello.',
                'as_user': False,
            }
            res = self.slack_client.api_call('chat.postMessage', **data)
            if not res['ok']:
                print('Failed')

