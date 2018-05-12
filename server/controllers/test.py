import logging
import asyncio

from aiohttp.web import json_response
from async_timeout import timeout

from server.mocks import review_requested_fixture
from server.lib.request_parser import ParserFactory
from server.lib.actions import GithubActionFactory

log = logging.getLogger('application')


async def test_ctr(request):
    # async with timeout(timeout=10) as timeout_ctx:
    action = GithubActionFactory.create_action(review_requested_fixture)
    user = await request.app['user_repository'].find_one(github_username=action.reviewer['login'])
    if not user:
        log.warning('Couldn\'t find user in our database with this github username: %s', action.reviewer['login'])
        return json_response({'ok': True})
    dm_id = user.slack_dm_id

    repo = await request.app['repo_repository'].find_one(repo_url=action.repo_url, subscribed_user_id=user.id)

    if not repo:
        log.warning('User %s is not subscribed for %s repository', action.reviewer, action.pr_url)
        return json_response({'ok': True})

    if not dm_id:
        dm_id = await request.app['slack_manager'].create_dm_id(slack_user_id=user.slack_id)
        await request.app['user_repository'].update(values={'slack_dm_id': dm_id}, id=user.id)

    message = action.to_slack_message(user.slack_id)
    log.info('Trying to send message to %s', user.slack_id)

    task = asyncio.ensure_future(request.app['slack_manager'].send(channel=dm_id, **message))
    task.add_done_callback(action.on_task_callback)
    # if timeout_ctx.expired:
    #     log.warning('Timeout reached in new github hook controller.')
    return json_response({'ok': True})


async def github_test_controller(request):
    parsed_request = await ParserFactory.parse(request)  # todo ParserFactory ?
    action = GithubActionFactory.create_action(parsed_request)
    if not action:
        log.warning('Received unknown action from GitHub: %s', parsed_request.get('action'))
        return json_response({'ok': True})
    message = action.to_slack_message()
    dm_id = await request.app['slack_manager'].create_dm_id(slack_user_id='U7N50A3NX')
    error = await request.app['slack_manager'].send(channel=dm_id,
                                                    **message)
    if error:
        log.error('Error sending msg to slack: %s', error)
        raise Exception(error)
    return json_response({'ok': True, 'error': None})
