from fastapi import APIRouter, HTTPException, Body
from passlib.hash import bcrypt_sha256
from schemas.user_schema import UserCreate, UserLogin
from utils.jwt_handler import create_access_token
from utils.db_helpers import create_record, read_record_by_email, read_record
import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])

"""Use bcrypt_sha256 so passwords of arbitrary length are supported.
bcrypt alone is limited to 72 bytes; bcrypt_sha256 pre-hashes with SHA-256
and avoids the 72-byte limitation while remaining compatible with bcrypt
strength and storage format. Keep `bcrypt` as a fallback so existing
bcrypt hashes remain verifiable.
"""

# pwd_context = CryptContext(schemes=["bcrypt_sha256", "bcrypt"], deprecated="auto")
# The `bcrypt_sha256` import is already present at the top.




@router.post("/register")
def register(user: UserCreate):
    logger.info(f"Registration attempt for email: {user.email}")
    logger.debug(f"Password length: {len(user.password)}")
    
    try:
        hashed = bcrypt_sha256.hash(user.password)
        logger.debug(f"Password hashed successfully")

        # Check if user already exists
        existing_user = read_record_by_email("users", user.email)
        if existing_user:
            raise HTTPException(status_code=409, detail="User with this email already exists")

        # Create record directly in Supabase
        created_user = create_record(
            table_name="users",
            supabase_data={
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "password_hash": hashed
            }
        )
        
        if not created_user:
            raise HTTPException(status_code=500, detail="Failed to register user")
        
        logger.info(f"User registered successfully: {user.email}, ID: {created_user.get('id')}")
        return {"message": "User registered"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Registration failed: {str(e)}")



@router.post("/login")
def login(
    user: UserLogin = Body(
        ..., examples={"default": {"summary": "Sample login", "value": UserLogin.Config.json_schema_extra["example"]}},
    ),
):
    logger.info(f"Login attempt for email: {user.email}")
    logger.debug(f"Password length: {len(user.password)}")
    
    # Query Supabase for existing user by email
    fetched_user = read_record_by_email(
        "users",
        user.email,
    )
    
    if not fetched_user:
        logger.warning(f"Login failed - User not found: {user.email}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Extract user data, handling both SQLAlchemy object and dictionary
    db_user_id = fetched_user.get("id")
    password_hash = fetched_user.get("password_hash")
    if not password_hash:
        logger.error(f"Password hash not found for user: {user.email}")
        raise HTTPException(status_code=500, detail="Internal server error")

    logger.debug(f"User found in database: {user.email}")
    logger.debug(f"Stored hash length: {len(password_hash)}")
    
    password_match = bcrypt_sha256.verify(user.password, password_hash)
    logger.debug(f"Password verification result: {password_match}")
    
    if not password_match:
        logger.warning(f"Login failed - Invalid password for user: {user.email}")
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    logger.info(f"Login successful for user: {user.email}")
    token = create_access_token({"user_id": db_user_id})
    logger.debug(f"Token created for user: {user.email}")
    return {"access_token": token, "user_id": db_user_id}
