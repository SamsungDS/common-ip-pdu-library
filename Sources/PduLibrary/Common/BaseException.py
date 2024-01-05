from PduLibrary.Common.GenericError import *


class BaseException(Exception):
    USR_ERR_MSG_PROP_NAME = '_AppErrorMessages'

    def __init__(self, err_code=None, *err_msg_params):
        self._ErrorMessages = dict()

        if generic_error_messages:
            self._ErrorMessages.update(generic_error_messages)

        if (hasattr(self, BaseException.USR_ERR_MSG_PROP_NAME)) and (
                getattr(self, BaseException.USR_ERR_MSG_PROP_NAME)):
            self._ErrorMessages.update(getattr(self, BaseException.USR_ERR_MSG_PROP_NAME))

        self._ErrorCode = None
        self._ErrorMessage = None

        if err_code is None:
            raise Exception()

        if (type(err_code) is str) and (err_msg_params is None):
            raise Exception(err_code)

        self._ErrorCode = err_code
        self._ErrorMessage = err_code

        if err_code in self._ErrorMessages:
            self._ErrorMessage = self._ErrorMessages[self._ErrorCode].format(*err_msg_params)

    def get_error_code(self):
        return self._ErrorCode

    def get_error_message(self):
        return self._ErrorMessage

    def __str__(self):
        if self._ErrorCode and self._ErrorMessage:
            return 'Error %s : %s' % (self._ErrorCode, self._ErrorMessage)
        else:
            return 'Undefined Exception'

    def __repr__(self):
        if self._ErrorCode and self._ErrorMessage:
            return 'Error %s : %s' % (self._ErrorCode, self._ErrorMessage)
        else:
            return 'Undefined Exception'
