from PduLibrary.Common.GenericError import GENERIC_ERR
from flask_restful import Resource, reqparse
from flask_restful_swagger import swagger
from werkzeug.exceptions import BadRequest

from PduLibrary.Controller.PduLibraryManager import PduLibraryManager
from PduLibrary.Exception.PduLibraryException import PduLibraryException


class GetVersion(Resource):
    STATUS_OK = 200
    INTERNAL_SERVER_ERROR = 500

    def __init__(self):
        self.test_executor_manager = PduLibraryManager.get_instance()
        self._arg_parser = reqparse.RequestParser()

    @swagger.operation(
        notes='API to say hello',
        nickname='hello',
        responseMessage=[
            {
                "code": 200,
                "message": "Success"
            },
            {
                "code": 500,
                "message": "Failure"
            }
        ]
    )
    def get(self):
        return_dict = dict()
        return_dict['ErrorCode'] = 0
        return_dict['Message'] = None
        return_dict['Data'] = None
        return_status_code = self.STATUS_OK

        try:
            version = self.test_executor_manager.get_version()
            return_dict["Message"] = "Success"
            return_dict['Data'] = dict()
            return_dict['Data']['version'] = version
        except PduLibraryException as e:
            return_dict['ErrorCode'] = e.get_error_code()
            return_dict['Message'] = e.get_error_message()
            return_dict['Data'] = None
            return_status_code = self.INTERNAL_SERVER_ERROR
        except BadRequest as e:
            return_dict['ErrorCode'] = GENERIC_ERR
            return_dict['Message'] = str(e)
            return_dict['Data'] = None
            return_status_code = e.code
        except Exception as e:
            return_dict['ErrorCode'] = GENERIC_ERR
            return_dict['Message'] = str(e)
            return_dict['Data'] = None
            return_status_code = self.INTERNAL_SERVER_ERROR
        return return_dict, return_status_code