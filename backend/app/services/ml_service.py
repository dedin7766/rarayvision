import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
import onnxruntime as ort
import os
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from backend.app.database import database as db
from backend.app.database import models as db_models
from backend.app.core.config import ANTI_SPOOF_MODEL_PATH, EMOTION_MODEL_PATH, CI_BASE_URL
import uuid
import requests


# JWT Secret Key
# ================= KONFIGURASI =================
# Path model anti-spoofing di folder models/ (satu level di atas backend)
# URL CodeIgniter API (Main Server)
# ===============================================



# --- 1. LOAD MODEL DETEKSI WAJAH (InsightFace) ---
print("⏳ Loading InsightFace Models...")
try:
    face_app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
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
        spoof_session = ort.InferenceSession(ANTI_SPOOF_MODEL_PATH, providers=['CPUExecutionProvider'])
        print(f"✅ Anti-Spoofing ONNX loaded successfully!")
    except Exception as e:
        print(f"❌ Error saat load ONNX: {e}")
else:
    print(f"⚠️ PERINGATAN: File {ANTI_SPOOF_MODEL_PATH} TIDAK DITEMUKAN! Fitur Liveness akan menggunakan fallback sederhana.")

print(f"⏳ Loading Emotion Model ({EMOTION_MODEL_PATH})...")
if os.path.exists(EMOTION_MODEL_PATH):
    try:
        emotion_session = ort.InferenceSession(EMOTION_MODEL_PATH, providers=['CPUExecutionProvider'])
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
    faces = db_session.query(db_models.Face).filter(db_models.Face.user_id == user_id).all()
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
    face = db_session.query(db_models.Face).filter(db_models.Face.user_id == user_id, db_models.Face.face_id == face_id).first()
    if face:
        face.name = name
        face.embedding = emb_json
        if image_url:
            face.image_url = image_url
        face.created_at = datetime.utcnow()
    else:
        face = db_models.Face(user_id=user_id, face_id=face_id, name=name, embedding=emb_json, image_url=image_url)
        db_session.add(face)
    db_session.commit()

def delete_face_from_db(db_session, user_id, face_id):
    face = db_session.query(db_models.Face).filter(db_models.Face.user_id == user_id, db_models.Face.face_id == face_id).first()
    if face:
        image_url = face.image_url
        db_session.delete(face)
        db_session.commit()
        
        # Hapus file fisik foto jika ada
        if image_url:
            import os
            filename = os.path.basename(image_url)
            # File mungkin disimpan di dua lokasi berbeda berdasarkan controller
            path1 = os.path.join(os.path.dirname(os.path.dirname(__file__)), "controllers", "uploads", "faces", filename)
            path2 = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "faces", filename)
            
            for p in [path1, path2]:
                if os.path.exists(p):
                    try:
                        os.remove(p)
                    except Exception as e:
                        print(f"Error deleting file {p}: {e}")
                        
        return True
    return False

# --- AUTHENTICATION DEPENDENCIES ---
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
    """Main liveness verification function — model: MiniFASNetV2 (80x80, 3-class)"""
    if spoof_session:
        try:
            # Scale 2.7 adalah standar MiniFASNet
            face_roi = crop_face_for_spoof(img, bbox, kps=kps, scale=2.7)
            if face_roi.size == 0 or face_roi.shape[0] < 10 or face_roi.shape[1] < 10:
                return 0.0, False
            # Resize ke 80x80 sesuai input model baru
            face_roi = cv2.resize(face_roi, (80, 80))

            # MiniFASNet menggunakan RAW BGR, tanpa divide by 255, tanpa normalization
            face_roi_bgr = face_roi.astype(np.float32)

            # HWC -> CHW -> NCHW
            face_roi_bgr = np.expand_dims(face_roi_bgr.transpose(2, 0, 1), axis=0)

            input_name = spoof_session.get_inputs()[0].name
            outputs = spoof_session.run(None, {input_name: face_roi_bgr})

            prediction = outputs[0]
            # Softmax
            exp_pred = np.exp(prediction - np.max(prediction, axis=1, keepdims=True))
            probs = exp_pred / np.sum(exp_pred, axis=1, keepdims=True)
            print(f"DEBUG PROBS: {probs[0]}")
            # index 1 = Real, index 0/2 = Spoof
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

    # 1. Search in RAM first (fast path)
    user_data = next((u for u in known_faces_db if str(u["id"]) == str(user_id)), None)
    target_embedding_db = None

    if user_data:
        target_embedding_db = user_data['embedding']
    else:
        # 2. If not found in RAM, fetch from the main server (CodeIgniter)
        try:
            url = f"{CI_BASE_URL}/get_face_by_id/{user_id}" 
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data and 'face_embedding' in data:
                    emb_list = json.loads(data['face_embedding'])
                    target_embedding_db = np.array(emb_list, dtype=np.float32)
        except Exception as e:
            print(f"Error fetch CI: {e}")

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

def process_recognize_multi(img, tenant_faces):
    """Logic for /recognize-multi and /recognize-live-multi endpoint (multi-face identification)"""

    faces = face_app.get(img)
    if len(faces) == 0:
        return {"status": "error", "message": "Face not detected"}
    
    results = []

    for target_face in faces:
        bbox = target_face.bbox.astype(int).tolist()
        landmarks = target_face.kps.astype(int).tolist()
        target_embedding = target_face.embedding
        
        base_data = {"bbox": bbox, "landmarks": landmarks}
        
        best_score = 0
        best_match = None

        for user in tenant_faces:
            sim = compute_similarity(target_embedding, user['embedding'])
            if sim > best_score:
                best_score = sim
                best_match = user
                
        if best_score > 0.50:
            results.append({
                "match": True,
                "data": {
                    "id": best_match['id'], 
                    "name": best_match['name'], 
                    "similarity": float(best_score),
                    **base_data
                }
            })
        else:
            results.append({
                "match": False,
                "message": "Face not recognized",
                "data": base_data
            })

    return {
        "status": "success",
        "mode": "identify_multi",
        "faces": results
    }

def process_global_face_login(img, db_session):
    """Logic for global face login"""
    faces = face_app.get(img)
    if len(faces) == 0:
        return {"status": "error", "message": "Face not detected"}
    
    if len(faces) > 1:
        return {"status": "error", "message": "Multiple faces detected. Please ensure only one face is visible."}
    
    target_face = faces[0]
    target_embedding = target_face.embedding
    
    # --- CHECK LIVENESS ---
    liveness_score, is_real = check_liveness(img, target_face.bbox, kps=target_face.kps)
    if not is_real:
        return {"status": "error", "message": f"Wajah palsu terdeteksi! (Spoof Score: {100 - (liveness_score*100):.1f}%)"}
    
    # Get all faces in the database that are for login (marked by name)
    all_faces = db_session.query(db_models.Face).filter(db_models.Face.name == 'Face Login Profile').all()
    best_score = 0
    best_match = None
    
    for row in all_faces:
        try:
            emb_list = json.loads(row.embedding)
            db_embedding = np.array(emb_list, dtype=np.float32)
            sim = compute_similarity(target_embedding, db_embedding)
            if sim > best_score:
                best_score = sim
                best_match = row
        except Exception as e:
            continue
            
    if best_score > 0.50 and best_match:
        # Get the User associated with this face
        user = db_session.query(db_models.User).filter(db_models.User.id == best_match.user_id).first()
        if user:
            return {
                "status": "success",
                "match": True,
                "user_id": user.id,
                "email": user.email,
                "similarity": float(best_score)
            }
        
    return { "status": "success", "match": False, "message": "Face not recognized or user not found" }

# ================= REST API ENDPOINTS =================

