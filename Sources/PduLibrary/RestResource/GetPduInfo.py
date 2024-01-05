from flask_restful import Resource, reqparse, fields
from flask_restful_swagger import swagger
from werkzeug.exceptions import BadRequest

from PduLibrary.Exception.PduLibraryException import PduLibraryException

from PduLibrary.Controller.PduLibraryManager import PduLibraryManager


@swagger.model
class GetPduInfoModel:
    resource_fields = {
        'manufacturer': fields.String(),
        'ip': fields.String(),
        'username': fields.String(),
        'password': fields.String()
    }

    required = ["manufacturer", "ip", "username", "password"]


class GetPduInfo(Resource):
    STATUS_OK = 200
    INTERNAL_SERVER_ERROR = 500

    def __init__(self):
        self._pdu_library_manager = PduLibraryManager.get_instance()
        self._arg_parser = reqparse.RequestParser()
        self._arg_parser.add_argument(
            'manufacturer',
            help='Manufacturer',
            required=True,
            location='json',
            dest='manufacturer',
            type=str
        )
        self._arg_parser.add_argument(
            'ip',
            help='IP',
            required=True,
            location='json',
            dest='ip',
            type=str
        )
        self._arg_parser.add_argument(
            'username',
            help='UserName',
            required=True,
            location='json',
            dest='username',
            type=str
        )
        self._arg_parser.add_argument(
            'password',
            help='Password',
            required=True,
            location='json',
            dest='password',
            type=str
        )

    @swagger.operation(
        notes='API to fetch the metadata of PDU',
        nickname='get_pdu_info',
        parameters=[
            {
                'name': 'body',
                'description': "API to fetch the metadata of PDU",
                'required': False,
                'allowMultiple': False,
                'dataType': GetPduInfoModel.__name__,
                'paramType': 'body'
            }
        ],
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
    def post(self):
        return_dict = dict()
        return_dict['ErrorCode'] = 0
        return_dict['Message'] = None
        return_dict['Data'] = None
        return_status_code = self.STATUS_OK

        try:
            args = self._arg_parser.parse_args()
            response = self._pdu_library_manager.get_pdu_info(args.manufacturer,
                                                              args.ip,
                                                              args.username,
                                                              args.password)
            return_dict['Data'] = response
        except PduLibraryException as e:
            return_dict['ErrorCode'] = e.get_error_code()
            return_dict['Message'] = e.get_error_message()
            return_dict['Data'] = None
            return_status_code = self.INTERNAL_SERVER_ERROR
        except BadRequest as e:
            return_dict['ErrorCode'] = self.INTERNAL_SERVER_ERROR
            return_dict['Message'] = str(e)
            return_dict['Data'] = None
            return_status_code = e.code
        except Exception as e:
            return_dict['ErrorCode'] = self.INTERNAL_SERVER_ERROR
            return_dict['Message'] = str(e)
            return_dict['Data'] = None
            return_status_code = self.INTERNAL_SERVER_ERROR
        return return_dict, return_status_code
