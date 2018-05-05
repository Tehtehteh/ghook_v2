import async_timeout
import aiohttp
import slacker

from urllib.parse import urlencode

from aioslacker import BaseAPI

Response = slacker.Response
Error = slacker.Error


async def patched_request(self, method, api, **kwargs):
        method = self.methods[method]

        kwargs.setdefault('params', {})
        kwargs.setdefault('timeout', None)

        if self.token:
            kwargs['params']['token'] = self.token

        kwargs['params'] = urlencode(kwargs['params'], doseq=True)

        if method == 'POST':
            files = kwargs.pop('files', None)

            if files is not None:
                data = kwargs.pop('data', {})

                _data = aiohttp.FormData()

                for k, v in files.items():
                    _data.add_field(k, open(v.name, 'rb'))

                for k, v in data.items():
                    if v is not None:
                        _data.add_field(k, str(v))

                kwargs['data'] = _data

        _url = slacker.API_BASE_URL.format(api=api)

        _request = self.session.request(method, _url, **kwargs)

        _response = None

        try:
            with async_timeout.timeout(self.timeout, loop=self.loop):
                _response = await _request

            _response.raise_for_status()

            text = await _response.text()
        finally:
            if _response is not None:
                await _response.release()

        response = Response(text)

        if not response.successful:
            raise Error(response.error)

        return response


def monkey_patch_base_api():
    BaseAPI._request = patched_request


monkey_patch_base_api()
