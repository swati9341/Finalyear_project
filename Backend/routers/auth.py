from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from passlib.hash import bcrypt_sha256
from database import SessionLocal
from models.user import User
from schemas.user_schema import UserCreate, UserLogin
from utils.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

"""Use bcrypt_sha256 so passwords of arbitrary length are supported.
bcrypt alone is limited to 72 bytes; bcrypt_sha256 pre-hashes with SHA-256
and avoids the 72-byte limitation while remaining compatible with bcrypt
strength and storage format. Keep `bcrypt` as a fallback so existing
bcrypt hashes remain verifiable.
"""

# pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from passlib.hash import bcrypt_sha256

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    print("RAW:", repr(user.password))
    print("LEN:", len(user.password))

    hashed = bcrypt_sha256.hash(user.password)
    print("HASHED:", hashed)

    db_user = User(email=user.email, password_hash=hashed)
    db.add(db_user)
    db.commit()

    return {"message": "User registered"}



@router.post("/login")
def login(
    user: UserLogin = Body(
        ..., examples={"default": {"summary": "Sample login", "value": UserLogin.Config.json_schema_extra["example"]}},
    ),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not bcrypt_sha256.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"user_id": db_user.id})
    return {"access_token": token}
