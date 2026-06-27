import os
import json
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from starlette.exceptions import HTTPException as StarletteHTTPException
import socketio

from backend.app.controllers import auth_controller, api_key_controller, face_controller
from backend.app.services.socket_service import sio
from backend.app.database.database import Base, engine

# Create DB Tables
Base.metadata.create_all(bind=engine)

fastapi_app = FastAPI(
    title="Raray Vision API",
    description="""
High-performance face recognition and computer vision API for face recognition,
liveness detection, face verification, and facial analysis.

Powered by:

\u2022 Buffalo-L (InsightFace)
\u2022 ArcFace (ResNet50)
\u2022 SCRFD Face Detection
\u2022 Custom ONNX Anti-Spoofing Model
\u2022 ONNX Runtime
\u2022 OpenCV
\u2022 NumPy
""",
    version="1.0.0",
    openapi_version="3.0.2",
    contact={"name": "Raray Vision Team", "url": "https://rarayvision.dfs.co.id"},
    servers=[{"url": "https://apirv.dfs.co.id", "description": "Production Server"}],
    docs_url=None,
    redoc_url=None,
)

# Mount Uploads directory
uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
fastapi_app.mount("/api/v1/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Setup CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths to hide from Swagger UI & ReDoc
_HIDDEN_PATHS = {"/api/v1/faces/login"}

# HTTP middleware: intercept /openapi.json and strip hidden paths from response
@fastapi_app.middleware("http")
async def filter_openapi_schema(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/openapi.json":
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        try:
            schema = json.loads(body)
            paths = schema.get("paths", {})
            for path in _HIDDEN_PATHS:
                paths.pop(path, None)
            
            # Remove orphaned tag groups
            used_tags = {
                tag
                for methods in paths.values()
                for op in methods.values()
                if isinstance(op, dict)
                for tag in op.get("tags", [])
            }
            if "tags" in schema:
                schema["tags"] = [t for t in schema["tags"] if t.get("name") in used_tags]

            # FIX: Swagger UI 5.x needs 'format': 'binary' to render file upload buttons
            # even though OpenAPI 3.1.0 uses contentMediaType. We inject it here.
            schemas = schema.get("components", {}).get("schemas", {})
            for schema_name, schema_obj in schemas.items():
                if "properties" in schema_obj:
                    for prop_name, prop_data in schema_obj["properties"].items():
                        if prop_data.get("contentMediaType") == "application/octet-stream":
                            prop_data["format"] = "binary"

            return JSONResponse(content=schema, status_code=response.status_code)
        except Exception:
            return JSONResponse(content=json.loads(body), status_code=response.status_code)
    return response

# Include Routers
fastapi_app.include_router(auth_controller.router)
fastapi_app.include_router(api_key_controller.router)
fastapi_app.include_router(face_controller.router)

_FAVICON = "/api/v1/uploads/favicon.png"

# Custom Swagger UI — branded header with Raray Vision logo
@fastapi_app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    template_path = Path(__file__).parent / "templates" / "swagger.html"
    return HTMLResponse(template_path.read_text())

# Custom ReDoc — branded header with Raray Vision logo
@fastapi_app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    template_path = Path(__file__).parent / "templates" / "redoc.html"
    return HTMLResponse(template_path.read_text())

def get_404_html():
    template_path = Path(__file__).parent / "templates" / "404.html"
    return template_path.read_text()

@fastapi_app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return HTMLResponse(content=get_404_html(), status_code=404)
    return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)

from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    name: str
    email: str
    message: str

@fastapi_app.post("/api/v1/feedback", tags=["General"], include_in_schema=False)
def submit_feedback(feedback: FeedbackRequest):
    print(f"Feedback received from {feedback.name} ({feedback.email}): {feedback.message}")
    return {"status": "success", "message": "Feedback received"}

from sqlalchemy.orm import Session
from fastapi import Depends
from backend.app.database.database import get_db
from backend.app.database.models import Face, ApiKey, User
from backend.app.core.deps import get_current_user
from sqlalchemy.sql import func

@fastapi_app.get("/health", tags=["System"])
def health_check(current_user: User = Depends(get_current_user)):
    return {"status": "ok", "message": "Raray Vision API is online"}

@fastapi_app.get("/version", tags=["System"])
def get_version(current_user: User = Depends(get_current_user)):
    return {
        "version": "1.0.0",
        "model": "buffalo_l",
        "engine": "InsightFace"
    }

@fastapi_app.get("/stats", tags=["System"])
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    registered_faces = db.query(func.count(Face.internal_id)).scalar() or 0
    total_requests = db.query(func.sum(ApiKey.usage_count)).scalar() or 0
    
    return {
        "registered_faces": registered_faces,
        "total_requests": int(total_requests),
        "today_requests": int(total_requests) # Placeholder for today
    }

# Setup Socket.IO App
app = socketio.ASGIApp(sio, fastapi_app)

# On Startup hook if needed
@fastapi_app.on_event("startup")
async def startup_event():
    print("🚀 FastAPI MVC Server Starting...")
    from backend.app.database.database import SessionLocal
    from backend.app.database.models import User
    from backend.app.core.security import get_password_hash
    
    db = SessionLocal()
    try:
        admin_email = "admin@rarayvision.dfs.co.id"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            print(f"Creating default admin user: {admin_email}")
            admin = User(
                email=admin_email,
                hashed_password=get_password_hash("askingme"),
                name="System Admin",
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
    except Exception as e:
        print(f"Failed to create default admin: {e}")
    finally:
        db.close()
