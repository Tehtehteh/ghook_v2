import os
import asyncio
import logging

from aiohttp import web


log = logging.getLogger('application')


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
    task = asyncio.ensure_future(await request.app['slack_manager'].send(channel=os.environ.get('ADMIN_ID'),
                                                                         text=f"Exception happened. Halp. Error: {exc}."
                                                                              f"Stack: {str(exc.info)}"))
    task.add_done_callback(lambda x: log.warning('Sent error to admin.') if not x.result().error else
                           log.error('Error sending slack message with error :0. Error: %s', x.result().error))

    return web.json_response({'ok': True})


error_middleware = exception_handler({
    'default': on_exception,
    500: on_exception
})
