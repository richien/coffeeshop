import os
import json
from flask import request
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = os.getenv('AUTH0_DOMAIN')
ALGORITHMS = os.getenv('ALGORITHMS')
API_AUDIENCE = os.getenv('API_AUDIENCE')

# AuthError Exception
'''
AuthError Exception.
A standardized way to communicate auth failure modes.
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
'''
Checks that the correct authorization header is sent
with the request i.e 'Bearer token'.
Returns the token part of the header.
'''


def get_token_auth_header():
    headers = request.headers.get('Authorization', None)
    if not headers:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header is missing.'
        }, 401)
    parts = headers.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': '"Bearer" missing from Authorization header.'
        }, 401)
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token missing from Authorization header.'
        }, 401)
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)
    token = parts[1]
    return token


'''
Checks jwks for an rsa key using a key ID in the token header.
Returns the rsa key.
'''


def get_rsa_key(token):
    JWKS_URL = os.getenv('JWKS_URL')
    try:
        jsonurl = urlopen(JWKS_URL)
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        if 'kid' not in unverified_header:
            raise AuthError({
                'code': 'invalid_header',
                'description': '"kid" missing from token header.'
            }, 401)

        for key in jwks['keys']:
            if key['kid'] == unverified_header['kid']:
                rsa_key = {
                    'kty': key['kty'],
                    'kid': key['kid'],
                    'use': key['use'],
                    'n': key['n'],
                    'e': key['e']
                }
        if not rsa_key:
            raise AuthError({
                'code': 'invalid_key',
                'description': 'Unable to find the appropriate key.'
            }, 401)
        return rsa_key
    except Exception:
        raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to verify token header.'
            }, 401)


'''
Verifies and decodes the JWT token.
Returns the payload.
'''


def verify_decode_jwt(token):
    rsa_key = get_rsa_key(token)
    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f'https://{AUTH0_DOMAIN}/'
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthError({
            'code': 'token_expired',
            'description': 'Token expired.'
        }, 401)
    except jwt.JWTClaimsError:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Incorrect claims. \
                            Please check the audience and issuer.'
        }, 401)
    except Exception:
        raise AuthError({
            'code': 'invalid_token',
            'description': 'Unable to decode token.'
        }, 400)


'''
Checks whether the token payload contains the permissions
neccessary to access a route.
Return true if correct permissions are found.
'''


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT'
        }, 400)
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'forbidden',
            'description': 'Permission not found'
        }, 403)
    return True


'''
Checks whether a request is from an authenticated user and
whether the user is permitted to access the requested resource.
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator
