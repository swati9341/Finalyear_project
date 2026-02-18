from datetime import datetime, timedelta
from jose import jwt
import os
import logging

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

logger.info(f"JWT Configuration - ALGORITHM: {ALGORITHM}, EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")
if not SECRET_KEY:
    logger.warning("SECRET_KEY environment variable is not set!")
if not ALGORITHM:
    logger.warning("ALGORITHM environment variable is not set!")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    logger.debug(f"Creating token for data: {data}")
    try:
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.debug(f"Token created successfully")
        return token
    except Exception as e:
        logger.error(f"Error creating token: {str(e)}", exc_info=True)
        raise
