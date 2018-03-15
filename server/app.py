import logging

from aiohttp import web
from aiohttp.web_response import json_response

import pprint

from .lib import Dispatcher

log = logging.getLogger('application')


async def github_hook(request):
    request_json = await request.json()
    action = request_json.get('action')
    if not action:
        log.warning('Received no action in request payload.')
        return json_response({'ok': False})
    Dispatcher.dispatch_action(action, payload=request_json)
    return json_response({'ok': True})


async def health(_):
    return json_response({'ok': True})


async def auth(request):
    # request_json = await request.json()
    print(await request.text())
    return json_response({'ok': True})


app = web.Application()
app.router.add_post('/poke', github_hook)
app.router.add_post('/auth', auth)
app.router.add_get('/_healthz', health)
