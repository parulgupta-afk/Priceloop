from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserOut
from app.services.auth_service import authenticate_user, register_user

router = APIRouter()


@router.post("/register", response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    user = register_user(db, payload.email, payload.password)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    token = create_access_token(subject=str(user.id), role=user.role.value)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Lets the frontend validate a stored token on page load without
    re-sending credentials -- if this 401s, the frontend should drop the
    token and show the login screen again."""
    return current_user
