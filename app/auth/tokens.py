from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app

from .errors import AuthError

ALGORITHM = "HS256"

def create_access_token(user):
    """Sign a short-lived JWT that says who the user is."""
    # firma (no cifrado) con hash

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.id), # PyJWT requires `sub` to be a string
        "username": user.username, # para mostrar en la página, no se consulta al servidor
        "iat": now, # fecha de emisión -> se verifica al decodificar
        "exp": now + timedelta(minutes=current_app.config["JWT_EXPIRES_MINUTES"]), # fecha de expiración, vence en -> se verifica al decodificar
        "iss": current_app.config["JWT_ISSUER"], # quién lo emitió -> se verifica al decodificar automáticamente PyJWT
    }

    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm=ALGORITHM)

def verify_decode_jwt(token):
    """Return the payload of a valid token or raise AuthError(401).
    `algorithms` is an explicit allow-list: never trust the `alg` the token
    claims for itself, or an attacker could send `"alg": "none"`.
    """

    try:
        return jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=[ALGORITHM],
            issuer=current_app.config["JWT_ISSUER"],
            options={"require": ["exp", "iat", "sub"]},
        )
    except jwt.ExpiredSignatureError:
        raise AuthError({"code": "token_expired", "description": "Token expired."}, 401)
    except jwt.InvalidTokenError:
        raise AuthError({"code": "invalid_token", "description": "Invalid token."}, 401)