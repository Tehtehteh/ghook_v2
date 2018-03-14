import logging

from environs import Env
from aiohttp import web
from server import app

logging.basicConfig(format='[%(asctime)s] [%(pathname)s:%(lineno)d] %(levelname)8s: %(message)s')
log = logging.getLogger('application')
log.setLevel(logging.DEBUG)

env = Env()
env.read_env()


def main():
    port = env.int('PORT')
    log.info('Starting application on %s', port)
    web.run_app(app, port=port)


if __name__ == '__main__':
    main()
