import json

from odoo import http, _
from odoo.http import request, route
from odoo.tools.config import config

import werkzeug
import jwt
import datetime
import json

import functools


secret_key = config.options.get('jwt_secret_key', 'Ark@na2019')

def _response(headers, body, status=200, request_type='http'):
    if request_type == 'json':
        response = {}
        response['error'] =[{
                    'code': status,
                    'message': body['message'],
            }]
        response['route'] = True
        return response
    try:
        fixed_headers = {str(k): v for k, v in headers.items()}
    except:
        fixed_headers = headers
    response = werkzeug.Response(response=json.dumps(body), status=status, headers=fixed_headers)
    return response

def token_required(**kw):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kw):
            headers = dict(request.httprequest.headers.items())
            request_type = request._request_type
            auth = headers.get('Authorization', None)
            #Ref https://github.com/mgonto/auth0-python-flaskapi-sample/blob/master/server.py
            if not auth:
                return {'error' : {'code': 403, 'message': 'No Authorization'}}
            parts = auth.split()
            if parts[0].lower() != 'bearer':
                return {'error' : {'code': 403, 'message': 'Authorization header must start with Bearer'}}
            elif len(parts) == 1:
                return {'error' : {'code': 403, 'message': 'Token not found'}}
            elif len(parts) > 2:
                return {'error' : {'code': 403, 'message': 'Authorization header must be Bearer + \s + token'}}
            token = parts[1]
            try:
                data = jwt.decode(token, secret_key)
                kw['uid'] = data['uid']
            except:
                return {'error' : {'code': 401, 'message': 'Token is invalid'}}
            response = f(*args, **kw)
            return response
        return wrapper
    return decorator

class ApiLogin(http.Controller):

    def _response(self, headers, body, status=200):
        try:
            fixed_headers = {str(k): v for k, v in headers.items()}
        except:
            fixed_headers = headers
        response = werkzeug.Response(response=body, status=status, headers=fixed_headers)
        return response

    @route('/api/v1/login', type='json', methods=['POST'], auth='public', csrf=False)
    def get_login(self, **kw):
        headers = dict(request.httprequest.headers.items())
        body = request.jsonrequest
        username = body.get('username', False)
        password = body.get('password', False)
        grant_type = body.get('grant_type', False)
        refresh_token = body.get('refresh_token', False)
        uid = body.get('user_id', False)
        if grant_type == "refresh_token" and (refresh_token and uid):
            request_result = request.env['rest.cr'].sudo().get_refresh_token(uid, refresh_token)
            if request_result:
                uid = request_result[0]
                username =request_result[1]
                token = jwt.encode({'uid': uid, 'user' : username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=86400)}, secret_key)
                result = {}
                result['token'] = token.decode('UTF-8')
                result['token_live'] = 86400
                result['refresh_token'] = refresh_token
                return {'result' : result}
            else:
                return {'error' : {'code': 401, 'message': 'Invalid Refresh Token'}}

        if username and password:
            uid = request.session.authenticate(request.session.db, username, password) #or request.cr.dbname for dbname
            if uid:
                token = jwt.encode({'uid': uid, 'user' : username, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(seconds=86400)}, secret_key)
                request_result = request.env['rest.cr'].login(uid)
                if request_result:
                    request_result['token'] = token.decode('UTF-8')
                    request_result['token_live'] = 86400
                    return {'result' : request_result}
