import os
import logging

from aiohttp import web

import database

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
    database.init()
    port = os.environ.get('PORT', 8080)
    log.info('Starting application on %s', port)
    web.run_app(app, port=port)


if __name__ == '__main__':
    main()
