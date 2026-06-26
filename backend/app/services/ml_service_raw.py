import uuid
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Depends, Header, Security
from fastapi.security import APIKeyHeader
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import socketio
import base64
import asyncio
from concurrent.futures import ThreadPoolExecutor
import onnxruntime as ort
import os
import requests 
import json
import sqlite3
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import backend.database as db
from backend.app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
# ================= KONFIGURASI =================
# Path model anti-spoofing di folder models/ (satu level di atas backend)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ANTI_SPOOF_MODEL_PATH = os.path.join(BASE_DIR, "models", "best_model_quantized.onnx")
EMOTION_MODEL_PATH = os.path.join(BASE_DIR, "models", "emotion-ferplus-8.onnx")
# ===============================================

from fastapi.staticfiles import StaticFiles

fastapi_app = FastAPI(
    title="Raray Vision API",
    description="Face recognition, liveness detection, and face comparison API.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

fastapi_app.mount("/api/v1/uploads", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "uploads")), name="uploads")

# Setup Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")
app = socketio.ASGIApp(sio, fastapi_app)

# Setup CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CHECK CUDA SUPPORT ---
import onnxruntime as ort_check
available_providers = ['CPUExecutionProvider']
if 'CUDAExecutionProvider' in ort_check.get_available_providers():
    available_providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
    print("🚀 CUDA GPU Detected! Running ML models on GPU.")
else:
    print("💻 No GPU detected. Running ML models on CPU.")

# --- 1. LOAD MODEL DETEKSI WAJAH (InsightFace) ---
print("⏳ Loading InsightFace Models...")
try:
    face_app = FaceAnalysis(name='buffalo_l', providers=available_providers)
    face_app.prepare(ctx_id=0, det_size=(640, 640))
    print("✅ InsightFace loaded successfully!")
except Exception as e:
    print(f"❌ Failed to load InsightFace: {e}")

# --- 2. LOAD MODEL ANTI-SPOOFING & EMOTION (ONNX) ---
spoof_session = None
emotion_session = None

print(f"⏳ Loading Anti-Spoofing Model ({ANTI_SPOOF_MODEL_PATH})...")
if os.path.exists(ANTI_SPOOF_MODEL_PATH):
    try:
        spoof_session = ort.InferenceSession(ANTI_SPOOF_MODEL_PATH, providers=available_providers)
        print("✅ Anti-Spoofing ONNX loaded successfully!")
    except Exception as e:
        print(f"❌ Error saat load ONNX: {e}")
else:
    print(f"⚠️ PERINGATAN: File {ANTI_SPOOF_MODEL_PATH} TIDAK DITEMUKAN! Fitur Liveness akan menggunakan fallback sederhana.")

print(f"⏳ Loading Emotion Model ({EMOTION_MODEL_PATH})...")
if os.path.exists(EMOTION_MODEL_PATH):
    try:
        emotion_session = ort.InferenceSession(EMOTION_MODEL_PATH, providers=available_providers)
        print("✅ Emotion ONNX loaded successfully!")
    except Exception as e:
        print(f"❌ Error saat load Emotion Model: {e}")
else:
    print(f"⚠️ PERINGATAN: File {EMOTION_MODEL_PATH} TIDAK DITEMUKAN!")

# Thread Pool untuk memproses gambar di background
thread_pool = ThreadPoolExecutor(max_workers=4)
client_buffers = {}

# --- DATABASE WAJAH ---
def get_tenant_faces(db_session, user_id):
    faces = db_session.query(db.Face).filter(db.Face.user_id == user_id).all()
    result = []
    for row in faces:
        try:
            emb_list = json.loads(row.embedding)
            result.append({
                "id": row.face_id,
                "name": row.name,
                "embedding": np.array(emb_list, dtype=np.float32)
            })
        except Exception as e:
            print(f"Error load face {row.face_id}: {e}")
    return result

def save_face_to_db(db_session, user_id, face_id, name, embedding, image_url=None):
    emb_json = json.dumps(np.array(embedding, dtype=np.float32).tolist())
    face = db_session.query(db.Face).filter(db.Face.user_id == user_id, db.Face.face_id == face_id).first()
    if face:
        face.name = name
        face.embedding = emb_json
        if image_url:
            face.image_url = image_url
        face.created_at = datetime.utcnow()
    else:
        face = db.Face(user_id=user_id, face_id=face_id, name=name, embedding=emb_json, image_url=image_url)
        db_session.add(face)
    db_session.commit()

def delete_face_from_db(db_session, user_id, face_id):
    face = db_session.query(db.Face).filter(db.Face.user_id == user_id, db.Face.face_id == face_id).first()
    if face:
        db_session.delete(face)
        db_session.commit()
        return True
    return False

# --- AUTHENTICATION DEPENDENCIES ---
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

def get_current_user(api_key: str = Depends(api_key_header), db_session: Session = Depends(db.get_db)):
    print(f"DEBUG AUTH: Received api_key={api_key}")
    if not api_key:
        print("DEBUG AUTH: Missing api_key")
        raise HTTPException(status_code=401, detail="API Key or Token is missing")
    if api_key.startswith("Bearer "):
        api_key = api_key.split(" ")[1]
        
    try:
        payload = jwt.decode(api_key, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        user = db_session.query(db.User).filter(db.User.id == user_id).first()
        if user:
            print(f"DEBUG AUTH: JWT valid for user_id={user_id}")
            return user
        print(f"DEBUG AUTH: JWT valid but user_id={user_id} not found in DB")
    except Exception as e:
        print(f"DEBUG AUTH: JWT decode exception: {e}")
        pass
        
    key_record = db_session.query(db.ApiKey).filter(db.ApiKey.key_string == api_key, db.ApiKey.status == "Active").first()
    if not key_record:
        print("DEBUG AUTH: Not a valid API key")
        raise HTTPException(status_code=401, detail="Invalid or revoked API Key")
    if key_record.expires_at and key_record.expires_at < datetime.utcnow():
        print("DEBUG AUTH: API key has expired")
        raise HTTPException(status_code=401, detail="API Key has expired")
        
    key_record.usage_count += 1
    db_session.commit()
    
    return key_record.user

class RegisterRequest(BaseModel):
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@fastapi_app.post("/api/v1/auth/register", include_in_schema=False)
def register_user(req: RegisterRequest, db_session: Session = Depends(db.get_db)):
    existing = db_session.query(db.User).filter(db.User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = db.get_password_hash(req.password)
    user = db.User(email=req.email, password_hash=hashed)
    db_session.add(user)
    db_session.commit()
    return {"status": "success", "user_id": user.id}

@fastapi_app.post("/api/v1/auth/login", include_in_schema=False)
def login_user(req: LoginRequest, db_session: Session = Depends(db.get_db)):
    user = db_session.query(db.User).filter(db.User.email == req.email).first()
    if not user or not db.verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = jwt.encode({"sub": str(user.id), "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)}, SECRET_KEY, algorithm=ALGORITHM)
    return {"status": "success", "token": token, "user_id": user.id, "email": user.email}

def get_user_from_token(authorization: str = Header(None), db_session: Session = Depends(db.get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db_session.query(db.User).filter(db.User.id == int(payload.get("sub"))).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@fastapi_app.get("/api/v1/keys", include_in_schema=False)
def get_api_keys(current_user: db.User = Depends(get_user_from_token)):
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

from typing import Optional

class CreateApiKeyRequest(BaseModel):
    name: str = "New Key"
    expires_in_days: Optional[int] = None

@fastapi_app.post("/api/v1/keys", include_in_schema=False)
def create_api_key(req: CreateApiKeyRequest, current_user: db.User = Depends(get_user_from_token), db_session: Session = Depends(db.get_db)):
    import secrets
    new_key = "rv_" + secrets.token_hex(16)
    
    expires_at = None
    if req.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=req.expires_in_days)

    k = db.ApiKey(user_id=current_user.id, key_string=new_key, name=req.name, expires_at=expires_at)
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

@fastapi_app.delete("/api/v1/keys/{key_id}", include_in_schema=False)
def revoke_api_key(key_id: str, current_user: db.User = Depends(get_user_from_token), db_session: Session = Depends(db.get_db)):
    k = db_session.query(db.ApiKey).filter(db.ApiKey.id == key_id, db.ApiKey.user_id == current_user.id).first()
    if k:
        db_session.delete(k)
        db_session.commit()
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Key not found")

# ================= HELPER FUNCTIONS =================

def _get_new_box(src_w, src_h, bbox, scale):
    x = bbox[0]
    y = bbox[1]
    box_w = bbox[2] - bbox[0]
    box_h = bbox[3] - bbox[1]

    scale = min((src_h-1)/box_h, min((src_w-1)/box_w, scale))

    new_width = box_w * scale
    new_height = box_h * scale
    center_x, center_y = box_w/2+x, box_h/2+y

    left_top_x = center_x-new_width/2
    left_top_y = center_y-new_height/2
    right_bottom_x = center_x+new_width/2
    right_bottom_y = center_y+new_height/2

    if left_top_x < 0:
        right_bottom_x -= left_top_x
        left_top_x = 0

    if left_top_y < 0:
        right_bottom_y -= left_top_y
        left_top_y = 0

    if right_bottom_x > src_w-1:
        left_top_x -= right_bottom_x-src_w+1
        right_bottom_x = src_w-1

    if right_bottom_y > src_h-1:
        left_top_y -= right_bottom_y-src_h+1
        right_bottom_y = src_h-1

    return int(left_top_x), int(left_top_y), int(right_bottom_x), int(right_bottom_y)

def crop_face_for_spoof(img, bbox, kps=None, scale=2.7):
    """Crop face area using official minivision logic"""
    src_h, src_w, _ = np.shape(img)
    left_top_x, left_top_y, right_bottom_x, right_bottom_y = _get_new_box(src_w, src_h, bbox, scale)

    cropped = img[left_top_y: right_bottom_y+1, left_top_x: right_bottom_x+1]

    # Lakukan rotasi alignment pada hasil crop jika ada KPS (wajah miring)
    if kps is not None and len(kps) >= 2:
        left_eye = kps[0]
        right_eye = kps[1]
        dy = right_eye[1] - left_eye[1]
        dx = right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dy, dx))
        
        # Hanya rotasi jika kemiringan lebih dari 5 derajat
        if abs(angle) > 5.0:
            crop_center = (cropped.shape[1] // 2, cropped.shape[0] // 2)
            M = cv2.getRotationMatrix2D(crop_center, angle, 1.0)
            cropped = cv2.warpAffine(cropped, M, (cropped.shape[1], cropped.shape[0]), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=[0, 0, 0])
            
    return cropped

def check_liveness(img, bbox, kps=None):
    """Main liveness verification function — model: MiniFASNetV2SE (128x128, 2-class)"""
    if spoof_session:
        try:
            # Scale 2.7 adalah standar MiniFASNet
            face_roi = crop_face_for_spoof(img, bbox, kps=kps, scale=2.7)
            if face_roi.size == 0 or face_roi.shape[0] < 10 or face_roi.shape[1] < 10:
                return 0.0, False
            # Resize ke 128x128 sesuai input model baru
            face_roi = cv2.resize(face_roi, (128, 128))

            # Konversi ke RGB karena ImageNet norm menggunakan urutan RGB
            face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
            face_roi = face_roi.astype(np.float32) / 255.0
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std  = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            face_roi = (face_roi - mean) / std

            # HWC -> CHW -> NCHW
            face_roi = np.expand_dims(face_roi.transpose(2, 0, 1), axis=0)

            input_name = spoof_session.get_inputs()[0].name
            outputs = spoof_session.run(None, {input_name: face_roi})

            prediction = outputs[0]
            # Softmax
            exp_pred = np.exp(prediction - np.max(prediction, axis=1, keepdims=True))
            probs = exp_pred / np.sum(exp_pred, axis=1, keepdims=True)
            print(f"DEBUG PROBS: {probs[0]}")
            # index 1 = Real, index 0 = Spoof
            real_score = float(probs[0][1])
            is_real = real_score > 0.55
            return real_score, is_real
        except Exception as e:
            print(f"Spoof Check Error: {e}")
            return 0.0, False
    else:
        # Fallback: multi-metric analysis tanpa model
        try:
            x1, y1, x2, y2 = bbox.astype(int)
            face_roi = img[y1:y2, x1:x2]
            if face_roi.size == 0: return 0.0, False
            
            gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            
            # Laplacian sharpness
            lap_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Color diversity — foto biasanya lebih flat warnanya
            hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)
            sat_std = np.std(hsv[:,:,1].astype(np.float32))
            
            # Gabungkan
            norm_lap = min(lap_score / 150.0, 1.0)
            norm_sat = min(sat_std / 40.0, 1.0)
            combined = (norm_lap * 0.6 + norm_sat * 0.4)
            
            is_real = combined > 0.35
            return float(combined), bool(is_real)
        except:
            return 0.0, False

def compute_similarity(embed1, embed2):
    return np.dot(embed1, embed2) / (np.linalg.norm(embed1) * np.linalg.norm(embed2))

# ================= LOGIC FUNCTIONS (THREAD SAFE) =================

def process_image_sync(img):
    """Logic untuk Socket.IO /analyze-face (General Analysis)"""
    faces = face_app.get(img)
    
    # --- VALIDASI JUMLAH WAJAH ---
    if len(faces) > 1:
        # Kembalikan list kosong atau status khusus agar frontend tidak bingung
        # Di sini kita return list kosong agar tidak ada kotak hijau yang digambar
        return [] 
        
    results = []
    
    for face in faces:
        liveness_score, is_real = check_liveness(img, face.bbox, kps=face.kps)
        gender = "Laki-laki" if face.gender == 1 else "Perempuan"
        
        raw_age = int(getattr(face, "age", 0)) if getattr(face, "age", 0) is not None and getattr(face, "age", 0) != -1 else 0
        if raw_age > 35: calibrated_age = raw_age - 9
        elif raw_age > 25: calibrated_age = raw_age - 6
        elif raw_age > 15: calibrated_age = raw_age - 3
        else: calibrated_age = raw_age
        
        results.append({
            "bbox": face.bbox.astype(int).tolist(),
            "gender": gender,
            "age": max(1, calibrated_age),
            "embedding": face.embedding.tolist(),
            "landmarks": face.kps.astype(int).tolist(),
            "liveness": {
                "score": liveness_score,
                "is_real": is_real,
                "method": "MiniFASNetV2" if spoof_session else "Laplacian"
            }
        })
    return results

def process_liveness_only(img):
    """Logic untuk Endpoint /check-liveness"""
    faces = face_app.get(img)
    
    if len(faces) == 0:
        return {"status": "error", "message": "Face not detected"}
    
    # --- VALIDASI JUMLAH WAJAH ---
    if len(faces) > 1:
        return {"status": "error", "message": "Multiple faces detected. Please use a single face image."}
    
    # Process only one face (faces[0])
    face = faces[0]
    
    score, is_real = check_liveness(img, face.bbox, kps=face.kps)
    
    return {
        "status": "success",
        "is_real": is_real,
        "score": score
    }

def process_register_live(img, check_spoof=True):
    """Register dari live camera"""
    faces = face_app.get(img)
    
    if len(faces) == 0:
        return {"status": "error", "message": "Face not detected"}

    if len(faces) > 1:
        return {"status": "error", "message": "Multiple faces detected. Please use a single face photo."}
    
    face = faces[0]
    score = 1.0
    
    if check_spoof:
        score, is_real = check_liveness(img, face.bbox, kps=face.kps)
        if not is_real:
            return {
                "status": "error",
                "message": f"Liveness check failed (score: {score:.2f}). Pastikan wajah asli di depan kamera dengan pencahayaan cukup."
            }

    return {
        "status": "success",
        "embedding": face.embedding.tolist(),
        "liveness_score": score
    }

def process_register_logic(img, check_spoof=True):
    """Logic untuk Endpoint /extract-face (Register)"""
    faces = face_app.get(img)
    
    if len(faces) == 0:
        return {"status": "error", "message": "Face not detected in the image"}

    if len(faces) > 1:
        return {"status": "error", "message": "Multiple faces detected. Please upload an image with a single face."}
    
    face = faces[0]
    score = 1.0

    # Liveness check opsional
    if check_spoof:
        score, is_real = check_liveness(img, face.bbox, kps=face.kps)
        if not is_real:
            return {"status": "error", "message": "Spoof face or screen detected"}

    return {
        "status": "success",
        "embedding": face.embedding.tolist(),
        "liveness_score": score
    }

def process_compare_logic(img, user_id, tenant_faces):
    """Logic for /compare-face endpoint (1:1 verification)"""
    if not user_id:
        user_id = "face_" + uuid.uuid4().hex[:8]
    known_faces_db = tenant_faces
    
    faces = face_app.get(img)
    
    if len(faces) == 0:
        return {"status": "error", "message": "Face not detected"}

    # --- VALIDASI JUMLAH WAJAH ---
    if len(faces) > 1:
        return {"status": "error", "message": "Multiple faces detected. Please ensure only one face is visible."}
    
    target_face = faces[0]
    
    # Liveness check disabled as requested
    # score_liveness, is_real = check_liveness(img, target_face.bbox, kps=target_face.kps)
    # if not is_real:
    #     return {"status": "error", "message": "Spoof face detected"}

    # 1. Search in RAM
    user_data = next((u for u in known_faces_db if str(u["id"]) == str(user_id)), None)
    target_embedding_db = None

    if user_data:
        target_embedding_db = user_data['embedding']

    if target_embedding_db is None:
        return {"status": "error", "message": "User face is not registered"}

    # 3. Bandingkan
    similarity = compute_similarity(target_face.embedding, target_embedding_db)
    
    THRESHOLD = 0.45 
    
    if similarity > THRESHOLD:
        return {
            "status": "success",
            "match": True,
            "similarity": float(similarity),
            "message": "Face matched"
        }
    else:
        return {
            "status": "success",
            "match": False,
            "similarity": float(similarity),
            "message": "Face did not match"
        }

def process_recognize_live(img, tenant_faces, mode="identify"):
    cv2.imwrite("/tmp/last_live_frame.jpg", img)
    """Logic for /recognize-live endpoint supporting multi-mode (identify, analyze, liveness)"""
    faces = face_app.get(img)
    if len(faces) == 0:
        return {"status": "error", "message": "Face not detected"}

    if len(faces) > 1:
        return {"status": "error", "message": "Multiple faces detected"}

    target_face = faces[0]
    bbox = target_face.bbox.astype(int).tolist()
    landmarks = target_face.kps.astype(int).tolist()
    
    base_data = {"bbox": bbox, "landmarks": landmarks}

    if mode == "analyze":
        gender_val = getattr(target_face, "gender", None)
        gender = "Male" if gender_val == 1 else "Female" if gender_val == 0 else "Unknown"
        
        raw_age = int(getattr(target_face, "age", 0)) if getattr(target_face, "age", 0) is not None and getattr(target_face, "age", 0) != -1 else 0
        if raw_age > 35: calibrated_age = raw_age - 9
        elif raw_age > 25: calibrated_age = raw_age - 6
        elif raw_age > 15: calibrated_age = raw_age - 3
        else: calibrated_age = raw_age

        return {
            "status": "success",
            "mode": mode,
            "data": {
                **base_data,
                "age": max(1, calibrated_age),
                "gender": gender
            }
        }
        
    if mode == "liveness":
        real_score, is_real = check_liveness(img, target_face.bbox, kps=target_face.kps)
        return {
            "status": "success",
            "mode": mode,
            "data": {
                **base_data,
                "liveness_score": float(real_score),
                "is_real": bool(is_real)
            }
        }
        
    if mode == "emotion":
        emotion_result = "Unknown"
        emotion_score = 0.0
        if emotion_session:
            x1, y1, x2, y2 = target_face.bbox.astype(int)
            raw_face_roi = img[y1:y2, x1:x2]
            if raw_face_roi.size > 0:
                gray_face = cv2.cvtColor(raw_face_roi, cv2.COLOR_BGR2GRAY)
                resized_face = cv2.resize(gray_face, (64, 64))
                input_data = np.expand_dims(np.expand_dims(resized_face, axis=0), axis=0).astype(np.float32)
                
                try:
                    outputs = emotion_session.run(None, {emotion_session.get_inputs()[0].name: input_data})
                    logits = outputs[0][0]
                    exp_pred = np.exp(logits - np.max(logits))
                    probs = exp_pred / np.sum(exp_pred)
                    
                    emotions = ['Neutral', 'Happy', 'Surprise', 'Sad', 'Angry', 'Disgust', 'Fear', 'Contempt']
                    best_idx = np.argmax(probs)
                    emotion_result = emotions[best_idx]
                    emotion_score = float(probs[best_idx])
                except Exception as e:
                    print(f"Error emotion inference: {e}")

        return {
            "status": "success",
            "mode": mode,
            "data": {
                **base_data,
                "emotion": emotion_result,
                "emotion_score": emotion_score
            }
        }

    if mode == "attributes":
        glasses_detected = False
        mask_detected = False
        
        x1, y1, x2, y2 = target_face.bbox.astype(int)
        raw_face_roi = img[max(0, y1):y2, max(0, x1):x2]
        
        if raw_face_roi.size > 0:
            gray_face = cv2.cvtColor(raw_face_roi, cv2.COLOR_BGR2GRAY)
            
            # Deteksi kacamata menggunakan edge density pada area mata (lebih akurat daripada Haar Cascade)
            h, w = gray_face.shape
            eyes_roi = gray_face[int(h*0.2):int(h*0.55), :]
            if eyes_roi.size > 0:
                blurred = cv2.GaussianBlur(eyes_roi, (5, 5), 0)
                edges = cv2.Canny(blurred, 50, 150)
                density = np.sum(edges > 0) / edges.size
                glasses_detected = bool(density > 0.05)
            
            # Heuristik sederhana deteksi masker menggunakan deteksi senyum/mulut
            # Jika hidung dan mulut tertutup, cascade smile/mulut biasanya gagal mendeteksi
            smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
            
            # Cek di bagian bawah wajah saja
            lower_face = gray_face[int(h/2):h, 0:w]
            smiles = smile_cascade.detectMultiScale(lower_face, scaleFactor=1.2, minNeighbors=3)
            
            # Jika tidak ada mulut/senyum yang terdeteksi di bagian bawah wajah, kita asumsikan pakai masker
            mask_detected = bool(len(smiles) == 0)

        return {
            "status": "success",
            "mode": mode,
            "data": {
                **base_data,
                "glasses": glasses_detected,
                "mask": mask_detected
            }
        }

    # Default to identify mode

    target_embedding = target_face.embedding
    best_score = 0
    best_match = None

    for user in tenant_faces:
        sim = compute_similarity(target_embedding, user['embedding'])
        if sim > best_score:
            best_score = sim
            best_match = user

    if best_score > 0.50:
        return {
            "status": "success", "match": True, "mode": mode,
            "data": {
                "id": best_match['id'], 
                "name": best_match['name'], 
                "similarity": float(best_score),
                **base_data
            }
        }
    else:
        return {
            "status": "success", 
            "match": False, 
            "mode": mode,
            "message": "Face not recognized",
            "data": base_data
        }

def process_recognize_logic(img, tenant_faces):
    """Logic for /recognize endpoint (1:N identification)"""

    faces = face_app.get(img)
    if len(faces) == 0:
        return {"status": "error", "message": "Face not detected"}
    
    # --- VALIDASI JUMLAH WAJAH ---
    if len(faces) > 1:
        return {"status": "error", "message": "Multiple faces detected."}
    
    target_face = faces[0]
    # Liveness check disabled as requested
    # score, is_real = check_liveness(img, target_face.bbox)
    # 
    # if not is_real:
    #     return {"status": "error", "message": "Spoof face detected"}

    target_embedding = target_face.embedding
    best_score = 0
    best_match = None

    for user in tenant_faces:
        sim = compute_similarity(target_embedding, user['embedding'])
        if sim > best_score:
            best_score = sim
            best_match = user
            
    if best_score > 0.50:
        return {
            "status": "success", "match": True,
            "data": { "id": best_match['id'], "name": best_match['name'], "similarity": float(best_score) }
        }
    else:
        return { "status": "success", "match": False, "message": "Face not recognized" }

# ================= REST API ENDPOINTS =================

@fastapi_app.get("/", include_in_schema=False)
def home():
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset=\"UTF-8\">
            <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
            <title>404 - Not Found</title>
            <style>
                body { font-family: Arial, sans-serif; background: #0f172a; color: #e2e8f0; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
                .card { text-align: center; padding: 2rem; border-radius: 12px; background: #111827; box-shadow: 0 10px 30px rgba(0,0,0,.35); }
                h1 { font-size: 3rem; margin-bottom: 0.5rem; }
                p { color: #cbd5e1; }
            </style>
        </head>
        <body>
            <div class=\"card\">
                <h1>404</h1>
                <p>This API endpoint is not available.</p>
            </div>
        </body>
        </html>
        """,
        status_code=404,
        media_type="text/html"
    )

# --- 1. CHECK LIVENESS (Verification Step 1) ---
