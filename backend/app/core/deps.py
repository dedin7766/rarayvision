from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
from datetime import datetime
import jwt

from backend.app.database.database import get_db
from backend.app.database import models as db_models
from backend.app.core.config import SECRET_KEY, ALGORITHM

api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def get_current_user(api_key: str = Depends(api_key_header), db_session: Session = Depends(get_db)):
    if not api_key:
        raise HTTPException(status_code=401, detail="API Key or Token is missing")
    if api_key.startswith("Bearer "):
        api_key = api_key.split(" ")[1]
        
    try:
        payload = jwt.decode(api_key, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = db_session.query(db_models.User).filter(db_models.User.id == user_id).first()
        if user:
            return user
    except Exception:
        pass
        
    key_record = db_session.query(db_models.ApiKey).filter(db_models.ApiKey.key_string == api_key, db_models.ApiKey.status == "Active").first()
    if not key_record:
        raise HTTPException(status_code=401, detail="Invalid or revoked API Key")
    if key_record.expires_at and key_record.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="API Key has expired")
        
    key_record.usage_count += 1
    db_session.commit()
    
    return key_record.user
