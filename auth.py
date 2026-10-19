"""Registration, sign-in and the dependency that resolves the current user."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db import LoginTakenError, User, create_user, get_user, get_user_by_login
from schemas import AuthRequest, TokenResponse, UserOut
from security import create_access_token, decode_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    """Return the user from the ``Authorization: Bearer <token>`` header.

    Raises:
        HTTPException: 401 if the token is missing, invalid or expired, or the
            user no longer exists.
    """
    user_id = decode_access_token(credentials.credentials) if credentials else None
    user = get_user(user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def _token_response(user: User) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: AuthRequest) -> TokenResponse:
    """Create an account and sign in right away."""
    try:
        user = create_user(login=data.login, password_hash=hash_password(data.password))
    except LoginTakenError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login is already taken")
    return _token_response(user)


@router.post("/login")
def login(data: AuthRequest) -> TokenResponse:
    """Sign in with a login and password."""
    user = get_user_by_login(data.login)
    if user is None:
        # Hash anyway so a missing login takes as long as a wrong password
        # and response time doesn't reveal which logins exist.
        hash_password(data.password)
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid login or password")
    return _token_response(user)


@router.get("/me")
def me(user: CurrentUser) -> UserOut:
    """Return the signed-in user."""
    return UserOut.model_validate(user)
