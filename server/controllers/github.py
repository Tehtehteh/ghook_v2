import logging

import asyncio

from aiohttp.web import json_response, HTTPFound, HTTPForbidden
from async_timeout import timeout

from server.lib import Dispatcher
from slackbot.bot import SlackBot

from server.lib.request_parser import ParserFactory
from server.lib.actions import GithubActionFactory

from server.lib.github_fetcher import GithubFetcher

log = logging.getLogger('application')


async def start_github_auth(request):
    log.info('Starting auth process...Request query: %s', request.query)
    redirect_uri = f'https://github.com/login/oauth/authorize?client_id={request.app["constants"]["gh_client_id"]}'
    redirect_uri += f'&redirect_uri={request.app["constants"]["gh_callback_url"]}?{request.query_string}'
    return HTTPFound(redirect_uri)


async def finalize_github_auth(request):
    log.info('Finalizing github auth...Request query: %s', request.query)
    if 'code' not in request.query:
        return HTTPForbidden()
    fetcher = GithubFetcher(code=request.query['code'], client_id=request.app['constants']['gh_client_id'],
                            client_secret=request.app['constants']['gh_client_secret'])
    github_login = await fetcher.process()
    slack_username = request.query['slack_user_name']
    user = await request.app['user_repository'].update(values={'github_username': github_login},
                                                       slack_username=slack_username)
    return json_response({'login': github_login})


async def new_github_hook(request):
    async with timeout(timeout=10) as timeout_ctx:
        parsed_request = await ParserFactory.parse(request)
        action = GithubActionFactory.create_action(parsed_request)
        if not action:
            log.warning('Unknown action received...')
            return json_response({'ok': True}, status=404)
        user = await request.app['user_repository'].find_one(github_username=action.reviewer['login'])
        if not user:
            log.warning('Couldn\'t find user in our database with this github username: %s', action.reviewer['login'])
            return json_response({'ok': True}, status=404)
        dm_id = user.slack_dm_id

        repo = await request.app['repo_repository'].find_one(repo_url=action.repo_url, subscribed_user_id=user.id)

        if not repo:
            log.warning('User %s is not subscribed for %s repository', action.reviewer, action.pr_url)
            return json_response({'ok': True}, status=404)

        if not dm_id:
            dm_id = await request.app['slack_manager'].create_dm_id(slack_user_id=user.slack_id)
            await request.app['user_repository'].update(values={'slack_dm_id': dm_id}, id=user.id)

        message = action.to_slack_message(user.slack_id)
        log.info('Trying to send message to %s', user.slack_id)

        task = asyncio.ensure_future(request.app['slack_manager'].send(channel=dm_id, **message))
        task.add_done_callback(action.on_task_callback)
    if timeout_ctx.expired:
        log.warning('Timeout reached in new github hook controller.')
        return json_response({'ok': False}, status=504)
    return json_response({'ok': True}, status=200)


@SlackBot.reportable
async def github_hook(request):
    request_json = await request.json()
    action = request_json.get('action')
    if not action:
        log.warning('Received no action in request payload.')
        return json_response({'ok': False})
    messages = Dispatcher.dispatch_action(action, payload=request_json)
    if not messages:
        return json_response({'ok': False})
    for msg in messages:
        SlackBot.send_notification(**msg)
    return json_response({'ok': True})
