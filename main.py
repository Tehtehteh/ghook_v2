import os
import logging

from aiohttp import web

import database

from server import create_web_app
from slackbot.bot import SlackBot, SlackManager

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
    app = create_web_app()
    web.run_app(app, port=port)


if __name__ == '__main__':
    main()
