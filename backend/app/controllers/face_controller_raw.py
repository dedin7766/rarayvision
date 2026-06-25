@fastapi_app.post("/api/v1/check-liveness")
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
@fastapi_app.post("/api/v1/compare-face")
async def compare_face_endpoint(
    user_id: str = Form(None),
    file: UploadFile = File(...),
    current_user: db.User = Depends(get_current_user),
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
@fastapi_app.post("/api/v1/extract-face")
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
@fastapi_app.post("/api/v1/register-face", summary="Register Face (with Liveness)")
async def register_face_endpoint(
    user_id: str = Form(None),
    user_name: str = Form(None),
    file: UploadFile = File(...),
    current_user: db.User = Depends(get_current_user),
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
        file_path = os.path.join(os.path.dirname(__file__), "uploads", "faces", filename)
        cv2.imwrite(file_path, img)
        image_url = f"/api/v1/uploads/faces/{filename}"
        
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
@fastapi_app.put("/api/v1/update-face", summary="Update Face")
async def update_face_endpoint(
    user_id: str = Form(...),
    user_name: str = Form(None),
    file: UploadFile = File(...),
    current_user: db.User = Depends(get_current_user),
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
        
        old_face = db_session.query(db.Face).filter(db.Face.user_id == current_user.id, db.Face.face_id == user_id).first()
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
@fastapi_app.delete("/api/v1/delete-face", summary="Delete Face")
async def delete_face_endpoint(
    user_id: str = Form(...),
    current_user: db.User = Depends(get_current_user),
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
@fastapi_app.get("/api/v1/list-faces", summary="List All Registered Faces")
async def list_faces_endpoint(
    current_user: db.User = Depends(get_current_user),
    db_session: Session = Depends(db.get_db)
):
    try:
        faces = db_session.query(db.Face).filter(db.Face.user_id == current_user.id).order_by(db.Face.created_at.desc()).all()
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
@fastapi_app.post("/api/v1/register-face-noliveness", summary="Register Face (no Liveness)")
async def register_face_noliveness_endpoint(
    user_id: str = Form(None),
    user_name: str = Form(None),
    file: UploadFile = File(...),
    current_user: db.User = Depends(get_current_user),
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
        file_path = os.path.join(os.path.dirname(__file__), "uploads", "faces", filename)
        cv2.imwrite(file_path, img)
        image_url = f"/api/v1/uploads/faces/{filename}"
        
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
@fastapi_app.post("/api/v1/register-face-live", summary="Register Face from Live Camera")
async def register_face_live_endpoint(
    user_id: str = Form(None),
    user_name: str = Form(None),
    file: UploadFile = File(...),
    current_user: db.User = Depends(get_current_user),
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
        file_path = os.path.join(os.path.dirname(__file__), "uploads", "faces", filename)
        cv2.imwrite(file_path, img)
        image_url = f"/api/v1/uploads/faces/{filename}"
        
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
@fastapi_app.post("/api/v1/recognize-live", summary="Recognize Face (Live Stream, multi-mode)")
async def recognize_live_endpoint(file: UploadFile = File(...), mode: str = Form("identify"), current_user: db.User = Depends(get_current_user), db_session: Session = Depends(db.get_db)):
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
@fastapi_app.post("/api/v1/recognize")
async def recognize_endpoint(file: UploadFile = File(...), current_user: db.User = Depends(get_current_user), db_session: Session = Depends(db.get_db)):
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

# --- 5. SOCKET WORKER ---
async def ai_worker():
    print("🚀 AI Worker Started...")
    while True:
        active_sids = list(client_buffers.keys())
        for sid in active_sids:
            if sid not in client_buffers: continue

            client = client_buffers[sid]
            
            if client['frame'] is not None and not client['processing']:
                client['processing'] = True
                frame_data = client['frame']
                client['frame'] = None 

                try:
                    nparr = np.frombuffer(frame_data, np.uint8)
                    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if img is not None:
                        loop = asyncio.get_running_loop()
                        results = await loop.run_in_executor(thread_pool, process_image_sync, img)
                        
                        await sio.emit("face_results", {
                            "status": "success", 
                            "faces": results
                        }, to=sid)
                
                except Exception as e:
                    print(f"Error processing {sid}: {e}")
                
                finally:
                    if sid in client_buffers:
                        client_buffers[sid]['processing'] = False
        
        await asyncio.sleep(0.01) 

# --- SOCKET EVENTS ---
@sio.event
async def connect(sid, environ):
    client_buffers[sid] = {'frame': None, 'processing': False}

@sio.event
async def disconnect(sid):
    if sid in client_buffers: del client_buffers[sid]

@sio.on("process_frame")
async def handle_frame(sid, data):
    if sid not in client_buffers: return
    try:
        if "," in data: _, encoded = data.split(",", 1)
        else: encoded = data
        data_bytes = base64.b64decode(encoded)
        client_buffers[sid]['frame'] = data_bytes
    except Exception: pass

# --- FEEDBACK ---
class FeedbackRequest(BaseModel):
    name: str
    email: str
    message: str

@fastapi_app.post("/api/v1/feedback")
def submit_feedback(req: FeedbackRequest):
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        feedback_file = os.path.join(os.path.dirname(__file__), "feedbacks.txt")
        with open(feedback_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.utcnow().isoformat()} - {req.name} ({req.email})\n{req.message}\n{'-'*40}\n")
    except Exception as e:
        print("Failed to save feedback to file:", e)
        
    msg = MIMEMultipart()
    msg['From'] = req.email
    msg['To'] = "mail@dfs.co.id"
    msg['Subject'] = f"Raray Vision API Feedback from {req.name}"
    msg.attach(MIMEText(f"Name: {req.name}\nEmail: {req.email}\n\nMessage:\n{req.message}", 'plain'))
    
    try:
        server = smtplib.SMTP('localhost', 25)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print("SMTP Error:", e)
        
    return {"status": "success", "message": "Feedback processed"}

# --- SERVER STARTUP ---
@fastapi_app.on_event("startup")
async def startup_event():
    asyncio.create_task(ai_worker())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
