from rest_framework.exceptions import APIException


class RelationAlreadyExist(APIException):
    status_code = 409
    default_detail = 'Relation already Exists.'
