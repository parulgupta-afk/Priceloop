from fastapi import APIRouter

router = APIRouter()


@router.post("/register")
def register():
    # TODO: hash password, create user, issue JWT
    raise NotImplementedError


@router.post("/login")
def login():
    # TODO: verify credentials, issue access + refresh tokens
    raise NotImplementedError
