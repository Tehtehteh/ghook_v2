import logging
import asyncio

from async_timeout import timeout

from aiohttp.web_response import json_response, Response

from server.lib.request_parser import ParserFactory
from slackbot.bot import SlackBot
from server.lib import Dispatcher
from server.lib.actions import SlackActionFactory

log = logging.getLogger('application')


async def gsign_command(request):
    parsed_request = await ParserFactory.parse(request)
    action = SlackActionFactory.create_action(parsed_request)
    user = await request.app['user_repository'].find_one(slack_username=action.username)
    if user and user.github_username:
        return Response(body=b'You are already registered ._.')
    with timeout(timeout=3) as timeout_ctx:
        if not action.channel_id:
            dm_id = await request.app['slack_manager'].create_dm_id(slack_user_id=action.user_id)
            user = await request.app['user_repository'].create(slack_id=action.user_id, slack_username=action.username,
                                                               slack_dm_id=dm_id)
            action.channel_id = dm_id
        else:
            user = await request.app['user_repository'].create(slack_id=action.user_id, slack_username=action.username,
                                                               slack_dm_id=action.channel_id)
        log.info('Created new user, yey. %s', user)
        message = action.to_slack_message()
        asyncio.ensure_future(request.app['slack_manager'].send(channel=action.channel_id, **message))
    if not timeout_ctx.expired:
        log.info('Successfuly registered new user within timeout. Hurray :}')
    return json_response({'ok': True})


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
