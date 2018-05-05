ALLOWED_CONTENT_TYPES = (
    'application/json',
    'application/x-www-form-urlencoded',
    'application/octet-stream'
)

class RequestAdapter(object):

    def __init__(self, payload):
        self.payload = payload

    @classmethod
    async def parse(cls, request):
        if request.content_type not in ALLOWED_CONTENT_TYPES:
            raise Exception('Not supported content-type received: %s', request)
        if request.content_type == 'application/json':
            return await cls.from_json(json_request=request)
        elif request.content_type == 'application/x-www-form-urlencoded':
            return cls.from_urlencoded(urlencoded_request=request)
        else:
            return request

    @classmethod
    def from_urlencoded(cls, urlencoded_request):
        return cls(payload=urlencoded_request.query)

    @classmethod
    async def from_json(cls, json_request):
        parsed = await json_request.json()
        return cls(payload=parsed)
