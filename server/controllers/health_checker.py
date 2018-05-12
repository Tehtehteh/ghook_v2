from aiohttp.web import json_response


async def health(request):
    user = await request.app['user_repository'].find(with_cache=True, id=4)
    return json_response({'ok': True})
