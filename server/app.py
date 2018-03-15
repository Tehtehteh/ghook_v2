import logging

from aiohttp import web
from aiohttp.web_response import json_response

log = logging.getLogger('application')


async def github_hook(_):  # todo
    return json_response({'ok': True})


async def health(_):
    log.info('Heyaa!')
    return json_response({'ok': True})

app = web.Application()
app.router.add_post('/poke', github_hook)
app.router.add_get('/_healthz', health)
