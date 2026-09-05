from sqlalchemy.orm import Session

from backend.app.core.security import create_access_token, hash_password, verify_password
from backend.app.models.user_model import User
from backend.app.repositories import backend_repo_user_repo as user_repository
from backend.app.schemas.user_schema import UserCreate


class EmailAlreadyRegisteredError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def register_user(db: Session, payload: UserCreate) -> User:
    if user_repository.get_user_by_email(db, payload.email):
        raise EmailAlreadyRegisteredError()

    return user_repository.create_user(
        db,
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = user_repository.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        # Deliberately the same error for "no such user" and "wrong password"
        # so the API doesn't leak which emails are registered.
        raise InvalidCredentialsError()
    return user


def issue_token_for(user: User) -> str:
    return create_access_token(subject=str(user.id))