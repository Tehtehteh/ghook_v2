import json

from urllib.parse import parse_qs


class GithubParser(object):

    @classmethod
    async def parse(cls, request):
        if request.headers['Content-Type'] == 'application/json':
            return await cls.from_json(request)
        elif request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
            return await cls.from_encoded(request)
        else:
            raise Exception('Not supported Content-Type header.')

    @classmethod
    async def from_json(cls, request):
        unmarshalled = await request.json()
        return unmarshalled

    @classmethod
    async def from_encoded(cls, request):
        text = await request.text()
        parsed_qs = parse_qs(text)
        parsed = json.loads(parsed_qs['payload'][0])
        return parsed
