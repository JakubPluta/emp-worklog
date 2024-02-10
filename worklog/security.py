import time

import jwt
from passlib.context import CryptContext

from worklog import config
from worklog.schemas.auth import AccessToken

JWT_ALGORITHM = config.settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_SECS = config.settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
REFRESH_TOKEN_EXPIRE_SECS = config.settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
PWD_CONTEXT = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=config.settings.SECURITY_BCRYPT_ROUNDS,
)


def create_jwt_token(
    subject: str | int, exp_secs: int, refresh: bool
) -> tuple[str, int, int]:
    """Creates jwt access or refresh token for user.

    Args:
        subject: anything unique to user, id or email etc.
        exp_secs: expire time in seconds
        refresh: if True, this is refresh token
    """

    issued_at = int(time.time())
    expires_at = issued_at + exp_secs

    to_encode: dict[str, int | str | bool] = {
        "issued_at": issued_at,
        "expires_at": expires_at,
        "sub": subject,
        "refresh": refresh,
    }
    encoded_jwt = jwt.encode(
        to_encode,
        key=config.settings.SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )
    return encoded_jwt, expires_at, issued_at


def generate_access_token_response(subject: str | int) -> AccessToken:
    """
    Generate an access token response for the given subject.

    Args:
        subject (str | int): The subject for which the access token is generated.

    Returns:
        AccessToken: The generated access token response.
    """

    access_token, expires_at, issued_at = create_jwt_token(
        subject, ACCESS_TOKEN_EXPIRE_SECS, refresh=False
    )
    refresh_token, refresh_expires_at, refresh_issued_at = create_jwt_token(
        subject, REFRESH_TOKEN_EXPIRE_SECS, refresh=True
    )
    return AccessToken(
        token_type="Bearer",
        access_token=access_token,
        expires_at=expires_at,
        issued_at=issued_at,
        refresh_token=refresh_token,
        refresh_token_expires_at=refresh_expires_at,
        refresh_token_issued_at=refresh_issued_at,
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if a plain password matches a hashed password.

    Args:
        plain_password (str): The plain password to be verified.
        hashed_password (str): The hashed password to compare with.

    Returns:
        bool: True if the plain password matches the hashed password, False otherwise.
    """
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate the hash value of a password.

    Args:
        password (str): The password to be hashed.

    Returns:
        str: The hash value of the password.
    """
    return PWD_CONTEXT.hash(password)
