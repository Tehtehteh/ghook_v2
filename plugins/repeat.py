from rtmbot.core import Plugin
import logging

log = logging.getLogger('slack')
stream_handler = logging.FileHandler('slack.log')
log.addHandler(stream_handler)
log.setLevel(logging.DEBUG)


class RepeatPlugin(Plugin):
    def process_message(self, data):
        if data['channel'].startswith("qwer"):
            log.info('Ayoooo')
            self.outputs.append(
                [data['channel'], 'from repeat1 "{}" in channel {}'.format(
                    data['text'], data['channel']
                )]
            )