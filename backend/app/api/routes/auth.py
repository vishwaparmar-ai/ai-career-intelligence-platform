from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_current_user
from backend.db.database import get_db
from backend.app.models.user_model import User
from backend.app.schemas.user_schema import Token, UserCreate, UserLogin, UserRead
from backend.app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    try:
        user = auth_service.register_user(db, payload)
    except auth_service.EmailAlreadyRegisteredError:
        raise HTTPException(status_code=400, detail="Email is already registered")

    return Token(access_token=auth_service.issue_token_for(user))


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    try:
        user = auth_service.authenticate_user(db, payload.email, payload.password)
    except auth_service.InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    return Token(access_token=auth_service.issue_token_for(user))


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user