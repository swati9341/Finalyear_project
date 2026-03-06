from fastapi import APIRouter

router = APIRouter()

@router.get("/", summary="Server Status Check")
async def home():
    """
    Returns a simple message to indicate that the server is running.
    Useful for health checks and deployment verification.
    """
    return {"message": "Server is running!"}