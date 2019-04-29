import os
import logging

from aiohttp import web

from database import create_database
from server import create_web_app
from slackbot.bot import SlackBot

logging.basicConfig(format='[%(asctime)s] [%(pathname)s:%(lineno)d] %(levelname)8s: %(message)s')
log = logging.getLogger('application')
log.setLevel(logging.DEBUG)


def main():
    from server.lib.utils import read_env
    debug = os.environ.get('DEBUG', False)
    if isinstance(debug, str):
        if debug.isdigit():
            debug = debug == '1'
        else:
            debug = debug.lower() != 'false'
    mode = 'development' if debug else 'production'
    if mode == 'development':
        read_env('.env')
    token = os.environ.get('SLACK_TOKEN')
    port = os.environ.get('PORT', 8080)
    if not token:
        log.error('Please provide slack token to use this bot')
        exit(1)
    log.info('Launching application is %s mode.', mode)

    SlackBot.init(token)
    create_database()
    app = create_web_app(debug)

    log.info('Starting application on %s', port)
    web.run_app(app, port=port)


if __name__ == '__main__':
    main()
