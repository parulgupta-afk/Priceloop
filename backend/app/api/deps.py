import uuid

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
        raw_id = payload.get("sub")
        user_id = uuid.UUID(raw_id)
    except (JWTError, ValueError, TypeError):
        # JWTError: bad signature/expired token. ValueError/TypeError: "sub" claim
        # wasn't a valid UUID (e.g. a tampered or malformed token) -- treat both
        # as an invalid token rather than letting a 500 leak internals.
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
