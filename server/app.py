import os
import logging

import sqlalchemy as sa

from aiohttp import web
from aiohttp.web_response import json_response, Response

from server.lib.request_adapter import RequestAdapter
from slackbot.bot import SlackBot, SlackManager
from .lib import Dispatcher


from database import User, Repository
from repositories import UserRepository

from .lib.actions.github_actions import GithubActionFactory
from .lib.request_parser import ParserFactory

log = logging.getLogger('application')


@SlackBot.reportable
async def github_hook(request):
    parsed_request = await RequestAdapter.parse(request)
    action = parsed_request.get('action')
    if not action:
        log.warning('Received no action in request payload.')
        return json_response({'ok': False})
    messages = Dispatcher.dispatch_action(action, payload=parsed_request)
    if not messages:
        return json_response({'ok': False})
    for msg in messages:
        SlackBot.send_notification(**msg)
    return json_response({'ok': True})


async def new_github_hook(request):
    parsed_request = await ParserFactory.parse(request)
    action = GithubActionFactory.create_action(parsed_request)
    if not action:
        log.warning('Received unknown action from GitHub: %s', parsed_request.get('action'))
        return json_response({'ok': True})
    log.info('Trying to find user...')
    user = UserRepository.get_user_by_github_username(action.reviewer['login'])
    if not user:
        log.warning('Couldn\'t find user in our database with this github email: %s', action.reviewer)
        return json_response({'ok': True})
    dm_id = user.slack_dm_id

    repo = sa.select([Repository]).where(sa.and_(Repository.c.repo_url == action.repo_url,
                                                 Repository.c.subscribed_user_id == user.id)).execute().fetchone()

    if not repo:
        log.warning('User %s is not subscribed for %s repository', action.reviewer, action.pr_url)
        return json_response({'ok': True})

    if not dm_id:
        dm_id = await request.app['slack_manager'].create_dm_id(slack_user_id=user.slack_id)
        User.update().where(User.c.id == user.id).values(slack_dm_id=dm_id).execute()

        log.info('Successfully set new dm id for user %s', User)

    message = action.to_slack_message(user.slack_id)
    log.info('Trying to send message to %s', user.slack_id)
    error = await request.app['slack_manager'].send(channel=dm_id,
                                                    **message)
    if error:
        log.error('Error sending msg to slack: %s', error)
        raise Exception(error)
    log.info('Successfuly sent message to %s', user.slack_id)
    return json_response({'ok': True, 'error': None})


async def test_slack(request):
    parsed_request = await ParserFactory.parse(request)  # todo ParserFactory ?
    action = GithubActionFactory.create_action(parsed_request)
    if not action:
        log.warning('Received unknown action from GitHub: %s', parsed_request.get('action'))
        return json_response({'ok': True})
    message = action.to_slack_message()
    dm_id = await request.app['slack_manager'].create_dm_id(slack_user_id='U7N50A3NX')  # todo danamic
    error = await request.app['slack_manager'].send(channel=dm_id,
                                                    **message)
    if error:
        log.error('Error sending msg to slack: %s', error)
        raise Exception(error)
    return json_response({'ok': True, 'error': None})


@SlackBot.reportable
async def slack_command(request):
    action = request.match_info.get('slack_command', None)
    if not action:
        log.warning('Got no action.')
        return Response(body='Bad action')
    payload = await request.text()
    result = Dispatcher.dispatch_action(action=action, payload=payload)
    if not result:
        return Response(body='Error!!')
    return json_response(result)


async def health(_):
    return json_response({'ok': True})


def setup_middlewares(app):
    def exception_handler(overrides):
        @web.middleware
        async def middleware(request, handler):
            try:
                response = await handler(request)
                override = overrides.get(response.status)
                if override is None:
                    return response
                else:
                    return await override(request)
            except web.HTTPException as exc:
                override = overrides.get(exc.status)
                if override is None:
                    raise
                else:
                    return await override(request, exc)
            except Exception as e:
                # info = traceback.format_exc(sys.exc_info())
                # e.info = info todo make traceback readable
                e.info = str(e)
                return await overrides.get('default')(request, e)

        return middleware

    async def on_exception(request, exc):
        await request.app['slack_manager'].send(channel=os.environ.get('ADMIN_ID'), text="Exception happened. Halp."
                                                                                         f"Error: {exc}."
                                                                                         f"Stack: {str(exc.info)}")
    error_middleware = exception_handler({
        'default': on_exception,
        500: on_exception
    })
    app.middlewares.append(error_middleware)


def create_web_app():
    app = web.Application()

    app.router.add_post('/poke', github_hook)
    app.router.add_post('/v2/poke', new_github_hook)
    app.router.add_get('/_healthz', health)
    app.router.add_post('/slack/{slack_command}', slack_command)

    # Packing constants inside application
    app['constants'] = {}
    app['constants']['slack_admin_id'] = os.environ.get('ADMIN_ID')
    app['constants']['slack_token'] = os.environ.get('SLACK_TOKEN')

    # Setting up SlackManager inside application
    app['slack_manager'] = SlackManager(token=app['constants']['slack_token'])

    # Handle application errors with reportable slack interface
    setup_middlewares(app)

    # Handle debug-only request-handlers
    debug = os.environ.get('DEBUG', False)
    if isinstance(debug, str):
        if debug.isdigit():
            debug = debug == '0'
        else:
            debug = debug.lower() != 'false'
    if debug:
        app.router.add_route(method='GET', path='/test', handler=test_slack)
        app.router.add_route(method='POST', path='/test', handler=test_slack)
    return app
