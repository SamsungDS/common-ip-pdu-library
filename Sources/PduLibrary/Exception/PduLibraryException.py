from PduLibrary.Common.BaseException import BaseException
from PduLibrary.Errors.ErrorCodes import ErrorMessages


class PduLibraryException(BaseException):
    def __init__(self, err_code=None, *err_msg_params):
        self._AppErrorMessages = ErrorMessages

        BaseException.__init__(self, err_code, *err_msg_params)