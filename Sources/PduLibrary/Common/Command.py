from cliff.command import Command
from PduLibrary.Common.BaseException import BaseException

from logging import getLogger


class Command(Command):
    def take_action(self, parsed_args):
        pass

    def run(self, parsed_args):
        try:
            return_value = self.take_action(parsed_args)
        except BaseException as e:
            _log = None

            if hasattr(self, 'LOG'):
                _log = self.LOG
            else:
                _log = getLogger(__name__)

            _log.error(str(e))
            return_value = e.get_error_code()

        return return_value
