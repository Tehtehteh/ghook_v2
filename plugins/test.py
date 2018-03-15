from rtmbot.core import Plugin


class TestPlugin(Plugin):
    def process_message(self, data):
        self.slack_client.api_call("users.list")
        self.outputs.append(
            [data['channel'], 'dssdfsdfdf']
        )

