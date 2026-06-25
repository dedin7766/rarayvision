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
    print(f"DEBUG AUTH: Received api_key={api_key}")
    if not api_key:
        print("DEBUG AUTH: Missing api_key")
        raise HTTPException(status_code=401, detail="API Key or Token is missing")
    if api_key.startswith("Bearer "):
        api_key = api_key.split(" ")[1]
        
    try:
        payload = jwt.decode(api_key, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = db_session.query(db_models.User).filter(db_models.User.id == user_id).first()
        if user:
            print(f"DEBUG AUTH: JWT valid for user_id={user_id}")
            return user
        print(f"DEBUG AUTH: JWT valid but user_id={user_id} not found in DB")
    except Exception as e:
        print(f"DEBUG AUTH: JWT decode exception: {e}")
        pass
        
    key_record = db_session.query(db_models.ApiKey).filter(db_models.ApiKey.key_string == api_key, db_models.ApiKey.status == "Active").first()
    if not key_record:
        print("DEBUG AUTH: Not a valid API key")
        raise HTTPException(status_code=401, detail="Invalid or revoked API Key")
    if key_record.expires_at and key_record.expires_at < datetime.utcnow():
        print("DEBUG AUTH: API key has expired")
        raise HTTPException(status_code=401, detail="API Key has expired")
        
    key_record.usage_count += 1
    db_session.commit()
    
    return key_record.user
