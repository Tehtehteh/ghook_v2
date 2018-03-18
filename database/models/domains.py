import enum


class RepoType(enum.Enum):
    """
    Class used in sa.Enum types for repositories types.
    If we want to support more, simply add new static property:
    mercurial = 'mercurial'
    """
    github = 'github'

