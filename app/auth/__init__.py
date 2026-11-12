"""JWT authentication: register, login and a decorator that requires a valid token.

Follows the structure of the Identity and Access Management course:
    AuthError -> error with its HTTP status code
    get_token_auth_header -> reads "Authorization: Bearer <token>"
    verify_decode_jwt -> checks signature, expiry and issuer
    requires_auth -> decorator: no valid token, no access

Instead of Auth0, this app issues its own tokens in POST /auth/login. The
client sends them back in the Authorization header on every request; no
cookies are involved.
"""

from .decorators import get_token_auth_header, requires_auth
from .errors import AuthError
from .tokens import create_access_token, verify_decode_jwt

__all__ = [
    "AuthError", # errors.py
    "create_access_token", # tokens.py
    "verify_decode_jwt", # tokens.py
    "get_token_auth_header", # decorators.py
    "requires_auth", # decorators.py
]