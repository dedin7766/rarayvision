from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets

from backend.app.schemas.schemas import CreateApiKeyRequest
from backend.app.database import database as db
from backend.app.database import models as db_models
from backend.app.core.config import SECRET_KEY, ALGORITHM
import jwt

router = APIRouter(prefix="/api/v1/keys", tags=["api_keys"])

def get_user_from_token(authorization: str = Header(None), db_session: Session = Depends(db.get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db_session.query(db_models.User).filter(db_models.User.id == int(payload.get("sub"))).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.get("", include_in_schema=False)
def get_api_keys(current_user: db_models.User = Depends(get_user_from_token)):
    return {
        "status": "success", 
        "keys": [{
            "id": k.id, 
            "key": k.key_string[:8] + "..." + k.key_string[-6:], 
            "name": k.name, 
            "status": k.status, 
            "usageCount": k.usage_count,
            "createdAt": k.created_at.isoformat(),
            "expiresAt": k.expires_at.isoformat() if k.expires_at else None
        } for k in current_user.api_keys]
    }

@router.post("", include_in_schema=False)
def create_api_key(req: CreateApiKeyRequest, current_user: db_models.User = Depends(get_user_from_token), db_session: Session = Depends(db.get_db)):
    new_key = "rv_" + secrets.token_hex(16)
    expires_at = None
    if req.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=req.expires_in_days)
    k = db_models.ApiKey(user_id=current_user.id, key_string=new_key, name=req.name, expires_at=expires_at)
    db_session.add(k)
    db_session.commit()
    db_session.refresh(k)
    return {
        "status": "success", 
        "key": {
            "id": k.id, 
            "key": k.key_string, 
            "name": k.name, 
            "status": k.status, 
            "usageCount": k.usage_count,
            "createdAt": k.created_at.isoformat(),
            "expiresAt": k.expires_at.isoformat() if k.expires_at else None
        }
    }

@router.delete("/{key_id}", include_in_schema=False)
def revoke_api_key(key_id: str, current_user: db_models.User = Depends(get_user_from_token), db_session: Session = Depends(db.get_db)):
    k = db_session.query(db_models.ApiKey).filter(db_models.ApiKey.id == key_id, db_models.ApiKey.user_id == current_user.id).first()
    if k:
        db_session.delete(k)
        db_session.commit()
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Key not found")
