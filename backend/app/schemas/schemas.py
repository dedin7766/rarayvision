from pydantic import BaseModel
from typing import Optional

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleLoginRequest(BaseModel):
    credential: str

class CreateApiKeyRequest(BaseModel):
    name: str = "New Key"
    expires_in_days: Optional[int] = None

class FeedbackRequest(BaseModel):
    name: str
    email: str
    message: str

class UpdateProfileRequest(BaseModel):
    name: str
    email: str
    store_images: Optional[bool] = False

class UpdatePasswordRequest(BaseModel):
    current_password: Optional[str] = None
    new_password: str
