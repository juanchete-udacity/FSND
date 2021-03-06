import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'dev-juanchete.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffeeshop'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
DONE implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    #get header from request
    auth_header = request.headers.get('authorization','None')
    token = None
    if not auth_header:
        raise AuthError({
            'description': 'No Authorization header supplied',
            'code':'UNAUTHORIZED'    
        },401)
    #split bearer from authorization
    parts = auth_header.split()
    #0 is the auth type(can be capitalized), 1 is the token
    if parts[0].lower() != 'bearer':
        #auth not supported
        raise AuthError({
            'description': 'Authorization method must be Bearer',
            'code':'INVALID_AUTH_METHOD'    
        },401)
    if len(parts)>1 and None != parts[1]:
        token = parts[1]
    
    return token
    

'''
DONE implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
def check_permissions(permission, payload):
    #If payload does not include the claims/permissions, error
    if 'permissions' not in payload:
        raise AuthError({
            'code':'INVALID_CLAIMS',
            'description':'Permissions are not included in the JWT token'
            },400)
    if permission not in payload['permissions']:
        #unathorized        
        raise AuthError({
            'code':'FORBIDDEN',
            'description': f'User does not have enough permissions to complete the operation. Required: ${permission}'
            },403)
    return True

'''
DONE implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
def verify_decode_jwt(token):
    
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'INVALID_HEADER',
            'description': 'Authorization malformed.'
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
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'TOKEN_EXPIRED',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'INVALID_CLAIMS',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'INVALID_HEADER',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'INVALID_HEADER',
                'description': 'Unable to find the appropriate key.'
            }, 400)

'''
DONE implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try: 
                payload = verify_decode_jwt(token)
            except:
                abort(401)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator

