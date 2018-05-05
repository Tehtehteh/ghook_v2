from abc import ABC, abstractmethod


class BaseAction(ABC):

    @abstractmethod
    def to_slack_message(self):
        pass
