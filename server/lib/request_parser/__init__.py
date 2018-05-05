import logging

from .github_parser import GithubParser

ALLOWED_CONTENT_TYPES = (
    'application/json',
    'application/x-www-form-urlencoded'
)

log = logging.getLogger('application')


class NotSupportedContentType(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class NoSuchParserExists(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class ParserFactory(object):

    @classmethod
    def get_concrete_parser(cls, request):
        if 'GitHub-Hookshot' in request.headers.get('User-Agent'):
            return GithubParser
        else:
            raise NoSuchParserExists

    @classmethod
    async def parse(cls, request):
        log.info('Trying to parse request.')
        if request.content_type not in ALLOWED_CONTENT_TYPES:
            log.error('No such content-type allowed: %s', request.content_type)
            raise NotSupportedContentType(
                f'Such content-type header is not supported. List of supported: {str(ALLOWED_CONTENT_TYPES)}')
        parser = ParserFactory.get_concrete_parser(request)
        parsed_request = await parser.parse(request)
        log.info('Successfully parsed request')
        return parsed_request
