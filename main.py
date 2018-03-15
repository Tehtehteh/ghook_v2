import os
import logging

import database

from aiohttp import web
from server import app
from slackbot.bot import SlackBot

logging.basicConfig(format='[%(asctime)s] [%(pathname)s:%(lineno)d] %(levelname)8s: %(message)s')
log = logging.getLogger('application')
log.setLevel(logging.DEBUG)


def main():
    token = os.environ.get('SLACK_TOKEN')
    if not token:
        exit(1)
    SlackBot.init(token)
    port = os.environ.get('PORT', 8080)
    log.info('Starting application on %s', port)
    # sb = bot.SlackBot(os.environ.get('SLACK_TOKEN'))
    # # sb.get_users()
    # # sb.send_notification(['U7N50A3NX', 'U96TFP1AL'])
    # sb.send_notification('U96TFP1AL')
    web.run_app(app, port=port)


if __name__ == '__main__':
    main()
