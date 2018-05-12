from urllib.parse import parse_qs

import aiohttp


class GithubFetcher(object):

    token_acquire_url = 'https://github.com/login/oauth/access_token'
    user_info_acquire_url = 'https://api.github.com/user'

    def __init__(self, code, client_id, client_secret):
        self.code = code
        self.client_id = client_id
        self.client_secret = client_secret

        self.access_token = None

    async def process(self):
        await self.get_token()
        github_login = await self.get_login()
        return github_login

    async def get_token(self):
        async with aiohttp.ClientSession() as session:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'code': self.code
            }
            async with session.post(url=self.token_acquire_url, data=data) as response:
                if response.status != 200:
                    raise Exception('Error getting token...')
                text = await response.text()
                self.access_token = parse_qs(text)['access_token'].pop()

    async def get_login(self):
        auth_headers = {'Authorization': f'token {self.access_token}'}
        async with aiohttp.ClientSession(headers=auth_headers) as session:
            async with session.get(url=self.user_info_acquire_url) as response:
                json_response = await response.json()
                return json_response['login']
