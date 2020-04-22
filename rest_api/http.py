from odoo.http import HttpRequest, JsonRequest, WebRequest, Response, Root
from odoo.http import SessionExpiredException, AuthenticationError, serialize_exception
import json
import odoo
import werkzeug
import simplejson
import logging
import datetime

from . import exceptions
_logger = logging.getLogger(__name__)



class ApiRequest(JsonRequest, WebRequest):
    """ Handler for the ``http`` request type.

    matched routing parameters, query string parameters, form_ parameters
    and files are passed to the handler method as keyword arguments.

    In case of name conflict, routing parameters have priority.

    The handler method's result can be:

    * a falsy value, in which case the HTTP response will be an
      `HTTP 204`_ (No Content)
    * a werkzeug Response object, which is returned as-is
    * a ``str`` or ``unicode``, will be wrapped in a Response object and
      interpreted as HTML

    .. _form: http://www.w3.org/TR/html401/interact/forms.html#h-17.13.4.2
    .. _HTTP 204: http://tools.ietf.org/html/rfc7231#section-6.3.5
    """
    _request_type = "json"

    def __init__(self, *args):
        super(JsonRequest, self).__init__(*args)

        self.jsonp_handler = None
        self.params = {}
        args = self.httprequest.args
        jsonp = args.get('jsonp')
        self.jsonp = jsonp
        request = None
        request_id = args.get('id')

        request = self.httprequest.stream.read()

        # Read POST content or POST Form Data named "request"
        if self.httprequest.method in ["POST", "PUT"]:
            try:
                self.jsonrequest = simplejson.loads(request)
            except simplejson.JSONDecodeError:
                msg = 'Invalid JSON data: %r' % (request,)
                _logger.error('%s: %s', self.httprequest.path, msg)
                raise werkzeug.exceptions.BadRequest(msg)

            # self.params = dict(self.jsonrequest.get("params", {}))
            # self.context = self.params.pop('context', dict(self.session.context))

    def _date_converter(self, o):
        if isinstance(o, datetime.datetime):
            return o.__str__()
        elif isinstance(o, datetime.date):
            return o.__str__()

    def _json_response(self, result=None, error=None):
        #Harus ditambahkan, karena secara default Odoo tidak memiliki error parameter pada JSON Endpoint
        #---------------------Begin of New Part----------------------------#
        status=200
        def process_result(result):
            status=200
            new_error = result.get('error')
            if new_error:
                error_code = new_error.get('code')
                if error_code:
                    status = error_code
            new_result = result.get('result')
            new_count = result.get('count')
            new_status = result.get('code', status)
            return new_result, new_count, new_error, new_status

        #---------------------End of New Part----------------------------#
        response = {
            'version': '1.0',
            }
        if error is not None:
            response['error'] = error
            status = error.get('code')
        if result is not None:
            result, count, error, status = process_result(result)
            if not result is None:
                response['result'] = result
            if not count is None:
                response['count'] = count
            if error :
                response['error'] = error

        mime = 'application/json'
        body = json.dumps(response, default = self._date_converter)

        #Harus ditambahkan, karena secara default odoo tidak memiliki STATUS CODE pada JSON Endpoint
        #---------------------Begin of New Part----------------------------#
        return Response(
                    response=body,
                    status=status,
                    headers=[('Content-Type', mime),
                                   ('Content-Length', len(body))])
        #---------------------End of New Part----------------------------#

    def _handle_exception(self, exception):
        """Called within an except block to allow converting exceptions
           to arbitrary responses. Anything returned (except None) will
           be used as response."""
        try:
            return WebRequest._handle_exception(self, exception)
        except Exception:
            if not isinstance(exception, (odoo.exceptions.Warning, SessionExpiredException)):
                _logger.exception("Exception during JSON request handling.")
            error = {
                    'code': 500,
                    'message': "Odoo Server Error",
                    #'data': serialize_exception(exception)
            }
            if isinstance(exception, AuthenticationError):
                error['code'] = 100
                error['message'] = "Odoo Session Invalid"
            if isinstance(exception, odoo.exceptions.AccessDenied):
                error['code'] = 401
                error['message'] = "Unauthorized"
            if isinstance(exception, SessionExpiredException):
                error['code'] = 100
                error['message'] = "Odoo Session Expired"
            if isinstance(exception, werkzeug.exceptions.NotFound):
                error['code'] = 404
                error['message'] = "Not found"
                error.pop('data', None)
            if isinstance(exception, werkzeug.exceptions.BadRequest):
                error['code'] = 400
                error['message'] = "Bad Request"
            if isinstance(exception, odoo.exceptions.AccessError):
                error['code'] = 403
                error['message'] = "Forbidden"
                error.pop('data', None)
            if isinstance(exception, werkzeug.exceptions.MethodNotAllowed):
                error['code'] = 405
                error['message'] = "MethodNotAllowed"
            if isinstance(exception, exceptions.RestException):
                error['code'] = exception.code
                error['message'] = exception.message
                error.pop('data', None)
            return self._json_response(error=error)


def get_request(self, httprequest):
    if ('/api/v1/' in httprequest.path) and (httprequest.mimetype == "application/json"):
        return ApiRequest(httprequest)
    if httprequest.args.get('jsonp'):
        return JsonRequest(httprequest)
    if httprequest.mimetype in ("application/json", "application/json-rpc"):
        return JsonRequest(httprequest)
    else:
        return HttpRequest(httprequest)

Root.get_request = get_request
