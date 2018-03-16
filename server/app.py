import logging

from aiohttp import web
from aiohttp.web_response import json_response, Response

from slackbot.bot import SlackBot
from .lib import Dispatcher

log = logging.getLogger('application')


async def github_hook(request):
    request_json = await request.json()
    action = request_json.get('action')
    if not action:
        log.warning('Received no action in request payload.')
        return json_response({'ok': False})
    result = Dispatcher.dispatch_action(action, payload=request_json)
    if result:
        SlackBot.send_notification(**result)
        return json_response({'ok': True})
    return json_response({'ok': False})


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

app = web.Application()
app.router.add_post('/poke', github_hook)
app.router.add_get('/_healthz', health)
app.router.add_post('/slack/{slack_command}', slack_command)
