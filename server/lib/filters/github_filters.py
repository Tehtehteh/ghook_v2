from repositories import UserRepository


def is_user_registered(username):
    return UserRepository.get_user_by_github_username(username) is not None


def is_user_subscribed(username, repository_url, chained=None):
    user = UserRepository.get_user_by_github_username(username)

def user_subscribed(user_id, repository_url):
    user = UserRepository.get_user_by_github_username(action.reviewer['login'])
    if not user:
        log.warning('Couldn\'t find user in our database with this github email: %s', action.reviewer)
        return json_response({'ok': True})
    dm_id = user.slack_dm_id

    repo = sa.select([Repository]).where(sa.and_(Repository.c.repo_url == action.repo_url,
                                                 Repository.c.subscribed_user_id == user.id)).execute().fetchone()

    if not repo:
        log.warning('User %s is not subscribed for %s repository', action.reviewer, action.pr_url)
        return json_response({'ok': True})