from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from passlib.hash import bcrypt_sha256
from database import SessionLocal
from models.user import User
from schemas.user_schema import UserCreate, UserLogin
from utils.jwt_handler import create_access_token
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

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
    logger.info(f"Registration attempt for email: {user.email}")
    logger.debug(f"Password length: {len(user.password)}")
    
    try:
        hashed = bcrypt_sha256.hash(user.password)
        logger.debug(f"Password hashed successfully")

        db_user = User(name=user.name, email=user.email, phone=user.phone, password_hash=hashed)
        db.add(db_user)
        db.commit()
        logger.info(f"User registered successfully: {user.email}")

        return {"message": "User registered"}
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")



@router.post("/login")
def login(
    user: UserLogin = Body(
        ..., examples={"default": {"summary": "Sample login", "value": UserLogin.Config.json_schema_extra["example"]}},
    ),
    db: Session = Depends(get_db),
):
    logger.info(f"Login attempt for email: {user.email}")
    logger.debug(f"Password length: {len(user.password)}")
    
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user:
        logger.warning(f"Login failed - User not found: {user.email}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    logger.debug(f"User found in database: {user.email}")
    logger.debug(f"Stored hash length: {len(db_user.password_hash)}")
    
    password_match = bcrypt_sha256.verify(user.password, db_user.password_hash)
    logger.debug(f"Password verification result: {password_match}")
    
    if not password_match:
        logger.warning(f"Login failed - Invalid password for user: {user.email}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    logger.info(f"Login successful for user: {user.email}")
    token = create_access_token({"user_id": db_user.id})
    logger.debug(f"Token created for user: {user.email}")
    return {"access_token": token, "user_id": db_user.id}
