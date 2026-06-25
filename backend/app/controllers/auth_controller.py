from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from backend.app.schemas.schemas import RegisterRequest, LoginRequest, UpdateProfileRequest
from backend.app.core.security import get_password_hash, verify_password, create_access_token
from backend.app.core.deps import get_current_user
from backend.app.database import database as db
from backend.app.database import models as db_models
from backend.app.services.ml_service import process_global_face_login, thread_pool
import asyncio
import cv2
import numpy as np

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.get("/me", include_in_schema=False)
def get_me(current_user: db_models.User = Depends(get_current_user)):
    return {
        "status": "success",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name or ""
        }
    }

@router.put("/update-profile", include_in_schema=False)
def update_profile(req: UpdateProfileRequest, db_session: Session = Depends(db.get_db), current_user: db_models.User = Depends(get_current_user)):
    current_user.name = req.name.strip()
    db_session.commit()
    db_session.refresh(current_user)
    return {
        "status": "success",
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name or ""
        }
    }


@router.post("/register", include_in_schema=False)
def register_user(req: RegisterRequest, db_session: Session = Depends(db.get_db)):
    existing = db_session.query(db_models.User).filter(db_models.User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = get_password_hash(req.password)
    user = db_models.User(email=req.email, name=req.name, password_hash=hashed)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return {"status": "success", "user_id": user.id}

@router.post("/login", include_in_schema=False)
def login_user(req: LoginRequest, db_session: Session = Depends(db.get_db)):
    user = db_session.query(db_models.User).filter(db_models.User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": str(user.id)})
    return {"status": "success", "token": token, "user_id": user.id, "email": user.email}

@router.post("/login-face", include_in_schema=False)
async def login_user_face(file: UploadFile = File(...), db_session: Session = Depends(db.get_db)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid or corrupted image")
        
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(thread_pool, process_global_face_login, img, db_session)
        
        if result.get("status") == "success" and result.get("match"):
            token = create_access_token({"sub": str(result.get("user_id"))})
            return {"status": "success", "token": token, "user_id": result.get("user_id"), "email": result.get("email")}
        else:
            raise HTTPException(status_code=401, detail=result.get("message", "Face not recognized"))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
