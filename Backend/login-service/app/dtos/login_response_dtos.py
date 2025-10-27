from pydantic import BaseModel
from datetime import datetime

class LoginResponse(BaseModel):
    statusCode: int
    message: str
    username: str
    access_token: str
    timestamp: datetime