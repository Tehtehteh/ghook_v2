import os
import logging

from aiohttp import web
from server import app

logging.basicConfig(format='[%(asctime)s] [%(pathname)s:%(lineno)d] %(levelname)8s: %(message)s')
log = logging.getLogger('application')
log.setLevel(logging.DEBUG)


def main():
    port = int(os.environ.get('PORT', 8080))
    log.info('Starting application on %s', port)
    web.run_app(app, port=port)


if __name__ == '__main__':
    main()
