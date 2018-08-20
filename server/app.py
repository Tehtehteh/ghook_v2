import os
import logging

from aiohttp import web

from slackbot.bot import SlackManager

from repositories import UserRepository, RepoRepository
from .middlewares import error_middleware
from .controllers import (
    new_github_hook, github_hook, start_github_auth, finalize_github_auth,
    health,
    slack_command, gsign_command,
    test_ctr
)

log = logging.getLogger('application')


def setup_middlewares(app):
    app.middlewares.append(error_middleware)


def create_web_app(debug):
    app = web.Application()

    # health endpoint
    app.router.add_get('/_healthz', health)

    # github handlers
    app.router.add_post('/poke', github_hook)
    app.router.add_post('/v2/poke', new_github_hook)
    app.router.add_get('/github/oauth/start', start_github_auth)
    app.router.add_get('/github/oauth/finalize', finalize_github_auth)

    # slack handlers
    app.router.add_post('/slack/gsignin', gsign_command)
    app.router.add_post('/slack/{slack_command}', slack_command)

    # Packing constants inside application
    app['constants'] = {}
    app['constants']['slack_admin_id'] = os.environ.get('ADMIN_ID')
    app['constants']['slack_token'] = os.environ.get('SLACK_TOKEN')
    app['constants']['gh_client_id'] = os.environ.get('GH_CLIENT_ID')
    app['constants']['gh_client_secret'] = os.environ.get('GH_CLIENT_SECRET')
    app['constants']['gh_callback_url'] = os.environ.get('GH_CALLBACK_URL')
    app['constants']['app_url'] = os.environ.get('APP_URL')
    app['constants']['force_ping_ids'] = os.environ.get('FORCE_PING_IDS', '').split(',')

    # Setting up SlackManager inside application
    app['slack_manager'] = SlackManager(token=app['constants']['slack_token'])

    # Setting up DbRepositories inside application
    app['user_repository'] = UserRepository()
    app['repo_repository'] = RepoRepository()

    # Handle application errors with reportable slack interface
    setup_middlewares(app)

    if debug:
        app.router.add_route(method='GET', path='/test', handler=test_ctr)
        app.router.add_route(method='POST', path='/test', handler=test_ctr)
    return app
