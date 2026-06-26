import os
import json
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
_HIDDEN_PATHS = {"/api/v1/register-login-face"}

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
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Raray Vision API — Swagger UI</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/png" href="/api/v1/uploads/favicon.png">
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css">
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

    /* ── Branded header ── */
    .rv-header {
      background: #0f172a;
      padding: 10px 24px;
      display: flex;
      align-items: center;
      gap: 12px;
      position: sticky;
      top: 0;
      z-index: 9999;
      border-bottom: 2px solid #6366f1;
    }
    .rv-header img  { height: 36px; width: auto; border-radius: 6px; }
    .rv-header span { color: #fff; font-weight: 700; font-size: 1.05rem; letter-spacing: -0.01em; }
    .rv-header small{ color: #94a3b8; font-size: 0.75rem; margin-left: 6px; }

    /* Hide default Swagger topbar */
    .swagger-ui .topbar { display: none !important; }
    .swagger-ui .info   { margin-top: 24px; }
  </style>
</head>
<body>
  <div class="rv-header">
    <img src="/api/v1/uploads/favicon.png" alt="Raray Vision Logo">
    <span>Raray Vision API <small>v1.0.0</small></span>
  </div>

  <div id="swagger-ui"></div>

  <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
  <script>
    window.onload = function () {
      SwaggerUIBundle({
        url: "/openapi.json",
        dom_id: "#swagger-ui",
        presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
        layout: "BaseLayout",
        deepLinking: true,
        showExtensions: true,
        showCommonExtensions: true,
        tryItOutEnabled: true
      })
    }
  </script>
</body>
</html>"""
    return HTMLResponse(html)

# Custom ReDoc — branded header with Raray Vision logo
@fastapi_app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    html = """<!DOCTYPE html>
<html>
<head>
  <title>Raray Vision API — ReDoc</title>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" type="image/png" href="/api/v1/uploads/favicon.png">
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }

    /* ── Branded header ── */
    .rv-header {
      background: #0f172a;
      padding: 10px 24px;
      display: flex;
      align-items: center;
      gap: 12px;
      height: 58px;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 9999;
      border-bottom: 2px solid #6366f1;
    }
    .rv-header img  { height: 36px; width: auto; border-radius: 6px; }
    .rv-header span { color: #fff; font-weight: 700; font-size: 1.05rem; letter-spacing: -0.01em; }
    .rv-header small{ color: #94a3b8; font-size: 0.75rem; margin-left: 6px; }

    /* ── Push ReDoc below our fixed header (58px) ── */
    /* Sidebar panel */
    .menu-content {
      top: 58px !important;
      height: calc(100vh - 58px) !important;
    }
    /* Right / main content panel */
    .api-content {
      margin-top: 58px !important;
    }
    /* Fallback: top-level redoc wrapper */
    redoc > div > div:last-child {
      margin-top: 58px;
    }
  </style>
</head>
<body>
  <div class="rv-header">
    <img src="/api/v1/uploads/favicon.png" alt="Raray Vision Logo">
    <span>Raray Vision API <small>v1.0.0</small></span>
  </div>

  <redoc spec-url="/openapi.json" hide-loading></redoc>

  <script src="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js"></script>
</body>
</html>"""
    return HTMLResponse(html)

def get_404_html():
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - Not Found | Raray Vision</title>
    <style>
        body { margin: 0; padding: 0; font-family: -apple-system, sans-serif; background: #0f172a; color: #f8fafc; display: flex; align-items: center; justify-content: center; height: 100vh; text-align: center; }
        .container { max-width: 500px; padding: 40px; background: #1e293b; border-radius: 12px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.5); }
        h1 { font-size: 80px; margin: 0; color: #6366f1; letter-spacing: -2px; }
        h2 { font-size: 24px; margin: 10px 0 20px; font-weight: 600; color: #e2e8f0; }
        p { color: #94a3b8; font-size: 15px; line-height: 1.6; margin-bottom: 30px; }
        a { display: inline-block; padding: 10px 24px; background: #3b82f6; color: #fff; text-decoration: none; font-weight: 500; border-radius: 8px; transition: background 0.2s; }
        a:hover { background: #2563eb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>404</h1>
        <h2>Endpoint Not Found</h2>
        <p>The API endpoint or page you are looking for does not exist.<br>Please refer to the official API documentation.</p>
        <a href="/docs">View API Documentation</a>
    </div>
</body>
</html>"""

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
from backend.database import get_db, Face, ApiKey, User
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
    print("\U0001f680 FastAPI MVC Server Starting...")
