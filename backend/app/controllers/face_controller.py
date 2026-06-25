from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Depends, Request
from sqlalchemy.orm import Session
import json
import base64
import asyncio
import cv2
import numpy as np
import uuid
import os

from backend.app.database import database as db
from backend.app.database import models as db_models
from backend.app.core.deps import get_current_user
from backend.app.services.ml_service import (
    process_liveness_only,
    process_compare_logic,
    process_register_logic,
    process_register_live,
    process_recognize_logic,
    process_recognize_live,
    get_tenant_faces,
    save_face_to_db,
    delete_face_from_db,
    thread_pool
)
from backend.app.schemas.schemas import FeedbackRequest

router = APIRouter(prefix="/api/v1")

@router.post(
    "/check-liveness",
    tags=["Liveness"],
    summary="Verify face liveness and detect spoof attacks",
    description="""
Verify whether a face is real or spoofed using a custom ONNX anti-spoofing model.

Supported detections:
- Printed photos
- Mobile screens
- Replay attacks
"""
)
async def check_liveness_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return {"status": "error", "message": "Invalid or corrupted image"}
        
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(thread_pool, process_liveness_only, img)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- 2. COMPARE FACE (Verification Step 2) ---
@router.post(
    "/compare-face",
    tags=["Recognition"],
    summary="Perform 1:1 face verification",
    description="""
Compare an uploaded face with a registered user identity
using ArcFace similarity matching.
"""
)
async def compare_face_endpoint(
    user_id: str = Form(None),
    file: UploadFile = File(...),
    current_user: db_models.User = Depends(get_current_user),
    db_session: Session = Depends(db.get_db)
):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return {"status": "error", "message": "Invalid or corrupted image"}

        tenant_faces = get_tenant_faces(db_session, current_user.id)
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(thread_pool, process_compare_logic, img, user_id, tenant_faces)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- 3. REGISTER (Extract Embedding) ---
@router.post(
    "/extract-face",
    tags=["Analysis"],
    summary="Extract face embeddings and facial landmarks",
    description="""
Extract:

- Face embeddings
- Facial landmarks
- Gender estimation
- Age estimation
"""
)
async def extract_face_endpoint(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return {"status": "error", "message": "Invalid or corrupted image"}
        
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(thread_pool, lambda: process_register_logic(img, check_spoof=False))
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- 3. REGISTER FACE (Save to Local Face DB) ---
@router.post(
    "/register-face",
    tags=["Registration"],
    summary="Register a new face with liveness verification"
)
async def register_face_endpoint(
    request: Request,
    user_id: str = Form(None),
    user_name: str = Form(None),
    file: UploadFile = File(...),
    current_user: db_models.User = Depends(get_current_user),
    db_session: Session = Depends(db.get_db)
):
    if not user_id:
        user_id = "face_" + uuid.uuid4().hex[:8]
    known_faces_db = get_tenant_faces(db_session, current_user.id)
    if any(str(item.get("id")) == str(user_id) for item in known_faces_db):
        return {"status": "error", "message": f"User ID '{user_id}' is already registered."}
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"status": "error", "message": "Invalid or corrupted image"}

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(thread_pool, lambda: process_register_logic(img, check_spoof=True))
        if result.get("status") != "success":
            return result

        embedding = np.array(result["embedding"], dtype=np.float32)
        final_name = user_name.strip() if user_name and user_name.strip() else user_id
        
        # Save image to disk
        filename = f"{current_user.id}_{user_id}.jpg"
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "faces")
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, filename)
        cv2.imwrite(file_path, img)
        base_url = str(request.base_url).rstrip("/") if request else ""
        image_url = f"{base_url}/api/v1/uploads/faces/{filename}"
        
        # (ID uniqueness check already performed above)
        known_faces_db.append({
            "id": user_id,
            "name": final_name,
            "embedding": embedding
        })
        save_face_to_db(db_session, current_user.id, user_id, final_name, embedding, image_url)

        return {
            "status": "success",
            "message": "Face registered and saved to database",
            "database": "PostgreSQL",
            "user_id": user_id,
            "user_name": final_name,
            "liveness_score": result.get("liveness_score"),
            "image_url": image_url,
            "total": len(known_faces_db)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- 3.1. UPDATE FACE ---
@router.put(
    "/update-face",
    tags=["Registration"],
    summary="Update an existing registered face"
)
async def update_face_endpoint(
    user_id: str = Form(...),
    user_name: str = Form(None),
    file: UploadFile = File(...),
    current_user: db_models.User = Depends(get_current_user),
    db_session: Session = Depends(db.get_db)
):
    if not user_id:
        return {"status": "error", "message": "user_id is required."}
    known_faces_db = get_tenant_faces(db_session, current_user.id)
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"status": "error", "message": "Invalid or corrupted image"}

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(thread_pool, lambda: process_register_logic(img, check_spoof=False))
        if result.get("status") != "success":
            return result

        embedding = np.array(result["embedding"], dtype=np.float32)
        
        old_face = db_session.query(db_models.Face).filter(db_models.Face.user_id == current_user.id, db_models.Face.face_id == user_id).first()
        final_name = user_name.strip() if user_name and user_name.strip() else (old_face.name if old_face else user_id)
        
        known_faces_db = [item for item in known_faces_db if str(item.get("id")) != str(user_id)]
        known_faces_db.append({
            "id": user_id,
            "name": final_name,
            "embedding": embedding
        })
        save_face_to_db(db_session, current_user.id, user_id, final_name, embedding)

        return {
            "status": "success",
            "message": "Face updated and saved to database",
            "database": "PostgreSQL",
            "id": user_id,
            "liveness_score": result.get("liveness_score"),
            "total": len(known_faces_db)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- 3.2. DELETE FACE ---
@router.delete(
    "/delete-face",
    tags=["Registration"],
    summary="Delete a registered face"
)
async def delete_face_endpoint(
    user_id: str = Form(...),
    current_user: db_models.User = Depends(get_current_user),
    db_session: Session = Depends(db.get_db)
):
    if not user_id:
        return {"status": "error", "message": "user_id is required."}
    known_faces_db = get_tenant_faces(db_session, current_user.id)
    try:
        before_count = len(known_faces_db)
        known_faces_db = [item for item in known_faces_db if str(item.get("id")) != str(user_id)]
        delete_face_from_db(db_session, current_user.id, user_id)

        return {
            "status": "success",
            "message": "Face deleted from database",
            "database": "PostgreSQL",
            "id": user_id,
            "deleted": before_count != len(known_faces_db),
            "total": len(known_faces_db)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- 4. LIST FACES ---
@router.get(
    "/list-faces",
    tags=["Management"],
    summary="List all registered faces"
)
async def list_faces_endpoint(
    current_user: db_models.User = Depends(get_current_user),
    db_session: Session = Depends(db.get_db)
):
    try:
        faces = db_session.query(db_models.Face).filter(db_models.Face.user_id == current_user.id).order_by(db_models.Face.created_at.desc()).all()
        result = []
        for f in faces:
            result.append({
                "id": f.face_id,
                "name": f.name,
                "image_url": f.image_url,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "updated_at": f.created_at.isoformat() if f.created_at else None
            })
        return {
            "status": "success",
            "total": len(result),
            "faces": result,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- REGISTER FACE LIVE (skip liveness check, untuk live camera) ---
@router.post(
    "/register-face-noliveness",
    tags=["Registration"],
    summary="Register a face without liveness verification"
)
async def register_face_noliveness_endpoint(
    request: Request,
    user_id: str = Form(None),
    user_name: str = Form(None),
    file: UploadFile = File(...),
    current_user: db_models.User = Depends(get_current_user),
    db_session: Session = Depends(db.get_db)
):
    if not user_id:
        user_id = "face_" + uuid.uuid4().hex[:8]
    known_faces_db = get_tenant_faces(db_session, current_user.id)
    if any(str(item.get("id")) == str(user_id) for item in known_faces_db):
        return {"status": "error", "message": f"User ID '{user_id}' is already registered."}
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"status": "error", "message": "Invalid image"}

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(thread_pool, lambda: process_register_logic(img, check_spoof=False))
        if result.get("status") != "success":
            return result

        embedding = np.array(result["embedding"], dtype=np.float32)
        final_name = user_name.strip() if user_name and user_name.strip() else user_id
        
        # Save image to disk
        filename = f"{current_user.id}_{user_id}.jpg"
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "faces")
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, filename)
        cv2.imwrite(file_path, img)
        base_url = str(request.base_url).rstrip("/") if request else ""
        image_url = f"{base_url}/api/v1/uploads/faces/{filename}"
        
        # (ID uniqueness check already performed above)
        known_faces_db.append({
            "id": user_id,
            "name": final_name,
            "embedding": embedding
        })
        save_face_to_db(db_session, current_user.id, user_id, final_name, embedding, image_url)

        return {
            "status": "success",
            "message": "Face registered successfully without liveness check",
            "user_id": user_id,
            "user_name": final_name,
            "image_url": image_url,
            "total": len(known_faces_db)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- REGISTER FACE LIVE (skip liveness check, untuk live camera) ---
@router.post(
    "/register-face-live",
    tags=["Registration"],
    summary="Register a face from live camera input"
)
async def register_face_live_endpoint(
    request: Request,
    user_id: str = Form(None),
    user_name: str = Form(None),
    file: UploadFile = File(...),
    current_user: db_models.User = Depends(get_current_user),
    db_session: Session = Depends(db.get_db)
):
    if not user_id:
        user_id = "face_" + uuid.uuid4().hex[:8]
    print(f"DEBUG REGISTER: user_id={user_id}, user_name={user_name}")
    known_faces_db = get_tenant_faces(db_session, current_user.id)
    if any(str(item.get("id")) == str(user_id) for item in known_faces_db):
        return {"status": "error", "message": f"User ID '{user_id}' is already registered."}
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"status": "error", "message": "Invalid or corrupted image"}

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(thread_pool, lambda: process_register_live(img, check_spoof=False))
        if result.get("status") != "success":
            return result

        embedding = np.array(result["embedding"], dtype=np.float32)
        final_name = user_name.strip() if user_name and user_name.strip() else user_id
        
        # Save image to disk
        filename = f"{current_user.id}_{user_id}.jpg"
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "faces")
        os.makedirs(uploads_dir, exist_ok=True)
        file_path = os.path.join(uploads_dir, filename)
        cv2.imwrite(file_path, img)
        base_url = str(request.base_url).rstrip("/") if request else ""
        image_url = f"{base_url}/api/v1/uploads/faces/{filename}"
        
        # (ID uniqueness check already performed above)
        known_faces_db.append({"id": user_id, "name": final_name, "embedding": embedding})
        save_face_to_db(db_session, current_user.id, user_id, final_name, embedding, image_url)

        return {
            "status": "success",
            "message": "Face registered and saved to database",
            "user_id": user_id,
            "user_name": final_name,
            "liveness_score": result.get("liveness_score"),
            "image_url": image_url,
            "total": len(known_faces_db)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- RECOGNIZE LIVE (skip liveness check, untuk live camera stream) ---
@router.post(
    "/recognize-live",
    tags=["Recognition"],
    summary="Real-time face recognition and analysis",
    description="""
Real-time face recognition supporting multiple modes:

- identify
- liveness
- emotion
- attributes
- analyze
"""
)
async def recognize_live_endpoint(file: UploadFile = File(...), mode: str = Form("identify"), current_user: db_models.User = Depends(get_current_user), db_session: Session = Depends(db.get_db)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"status": "error", "message": "Invalid or corrupted image"}

        loop = asyncio.get_running_loop()
        tenant_faces = get_tenant_faces(db_session, current_user.id)
        result = await loop.run_in_executor(thread_pool, process_recognize_live, img, tenant_faces, mode)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}
@router.post(
    "/recognize",
    tags=["Recognition"],
    summary="Recognize a face against registered identities",
    description="""
Perform 1:N face identification using ArcFace embeddings
powered by Buffalo-L (InsightFace).
"""
)
async def recognize_endpoint(file: UploadFile = File(...), current_user: db_models.User = Depends(get_current_user), db_session: Session = Depends(db.get_db)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return {"status": "error", "message": "Invalid or corrupted image"}
        
        loop = asyncio.get_running_loop()
        tenant_faces = get_tenant_faces(db_session, current_user.id)
        result = await loop.run_in_executor(thread_pool, process_recognize_logic, img, tenant_faces)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- REGISTER LOGIN FACE (dedicated endpoint for face login registration) ---
@router.post("/register-login-face", include_in_schema=False)
async def register_login_face_endpoint(
    request: Request,
    file: UploadFile = File(...),
    current_user: db_models.User = Depends(get_current_user),
    db_session: Session = Depends(db.get_db)
):
    """Register or update the user's login face. face_id = user's actual ID."""
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"status": "error", "message": "Invalid or corrupted image"}

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(thread_pool, lambda: process_register_live(img, check_spoof=False))
        if result.get("status") != "success":
            return result

        embedding = np.array(result["embedding"], dtype=np.float32)
        face_id = str(current_user.id)
        face_name = "Face Login Profile"
        
        # Save image to the correct uploads directory
        uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "faces")
        os.makedirs(uploads_dir, exist_ok=True)
        filename = f"{current_user.id}_login_face.jpg"
        file_path = os.path.join(uploads_dir, filename)
        cv2.imwrite(file_path, img)
        base_url = str(request.base_url).rstrip("/") if request else ""
        image_url = f"{base_url}/api/v1/uploads/faces/{filename}"
        
        # Upsert: save_face_to_db already handles update if face_id exists
        save_face_to_db(db_session, current_user.id, face_id, face_name, embedding, image_url)

        return {
            "status": "success",
            "message": "Login face registered successfully",
            "face_id": face_id,
            "name": face_name,
            "image_url": image_url,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
