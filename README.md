# Raray Vision

Raray Vision is an open-source, self-hosted face recognition API built with FastAPI, InsightFace, ArcFace, and ONNX Runtime. It provides production-ready endpoints for face recognition, liveness detection, face verification, and facial analysis.

The name comes from the Sundanese word **Raray**, meaning face.

---

## Features

- 1:N face recognition using ArcFace (ResNet50) embeddings
- 1:1 face verification (cosine similarity matching)
- Anti-spoofing liveness detection using a custom ONNX model
- Face registration, update, and deletion with persistent storage
- Real-time multi-mode face recognition via live camera stream
- Face embedding and landmark extraction
- API key authentication per tenant
- JWT-based user authentication
- Socket.IO real-time event support
- Swagger UI and ReDoc documentation included
- Fully self-hostable via Docker or bare metal

---

## AI and Computer Vision Stack

- **Buffalo-L (InsightFace)** — Face recognition, landmarks, age, and gender estimation
- **ArcFace (ResNet50)** — 512-dimensional facial embeddings for high-accuracy matching
- **SCRFD** — Real-time face detection
- **Custom ONNX Anti-Spoofing Model** — Liveness verification and spoof attack detection
- **ONNX Runtime** — High-performance model inference engine
- **OpenCV** — Computer vision and image processing
- **NumPy** — Numerical and vector computations

---

## How Face Embedding Works

Raray Vision uses the ArcFace algorithm with a ResNet50 backbone. ArcFace applies an Additive Angular Margin Loss during training, which forces the model to learn highly discriminative features by maximizing the angular distance between different identities in the embedding space.

Each detected face is aligned using 5-point facial landmarks, then passed through the ResNet50 network to produce a compact 512-dimensional float32 vector (embedding). This vector is a unique numerical "fingerprint" of the face.

Matching is performed using Cosine Similarity — measuring the angle between two embedding vectors. A similarity score above 0.45 (1:1 verification) or 0.50 (1:N identification) indicates a positive match.

---

## Technology Stack

| Layer | Technology |
|---|---|
| Backend Framework | FastAPI + Uvicorn |
| Real-time | Python Socket.IO |
| Database | MySQL / MariaDB via SQLAlchemy |
| Auth | JWT (PyJWT) + Passlib bcrypt |
| Frontend | Vue 3 + Vite |
| Process Manager | PM2 |
| Reverse Proxy | Nginx |

---

## Project Structure

```
rarayvision/
  backend/
    main.py                  — FastAPI application entry point
    app/
      controllers/           — Route handlers (face, auth, api key)
      services/              — Business logic and ML inference
      database/              — SQLAlchemy models and session
      schemas/               — Pydantic request/response schemas
      core/                  — Security, JWT, dependencies
    models/                  — ONNX model files
    uploads/                 — Stored face images
  frontend/
    src/
      views/                 — Vue page components
      components/            — Shared UI components
      services/              — API service layers
  requirements.txt
  ecosystem.config.js        — PM2 process config
  Dockerfile
  docker-compose.yml
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | /api/v1/check-liveness | Verify face liveness / anti-spoofing |
| POST | /api/v1/recognize | 1:N face identification |
| POST | /api/v1/compare-face | 1:1 face verification |
| POST | /api/v1/recognize-live | Real-time multi-mode recognition |
| POST | /api/v1/register-face | Register face with liveness check |
| POST | /api/v1/register-face-live | Register face from live camera |
| POST | /api/v1/register-face-noliveness | Register face without liveness |
| PUT | /api/v1/update-face | Update registered face |
| DELETE | /api/v1/delete-face | Delete registered face |
| GET | /api/v1/list-faces | List all registered faces |
| POST | /api/v1/extract-face | Extract embeddings and landmarks |

Full interactive documentation:
- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

---

## Self-Hosting: Option 1 — Docker (Recommended)

### Prerequisites

- Docker Engine 24+
- Docker Compose v2+
- MySQL or MariaDB instance (can be included via compose)

### 1. Clone the repository

```bash
git clone https://github.com/dedin7766/rarayvision.git
cd rarayvision
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=mysql+pymysql://raray:yourpassword@db:3306/rarayvision
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 3. Create the Dockerfile

If not already present, create `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "5000"]
```

### 4. Create docker-compose.yml

```yaml
version: "3.9"

services:
  db:
    image: mariadb:10.11
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: rarayvision
      MYSQL_USER: raray
      MYSQL_PASSWORD: yourpassword
    volumes:
      - db_data:/var/lib/mysql
    ports:
      - "3306:3306"

  backend:
    build: .
    restart: unless-stopped
    depends_on:
      - db
    ports:
      - "5000:5000"
    env_file:
      - .env
    volumes:
      - ./backend/uploads:/app/backend/uploads
      - ./backend/models:/app/backend/models

volumes:
  db_data:
```

### 5. Build and start

```bash
docker compose up --build -d
```

### 6. Verify the service is running

```bash
curl http://localhost:5000/
# Expected: {"message":"Raray Vision API MVC is running"}
```

### 7. Access documentation

- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

---

## Self-Hosting: Option 2 — Bare Metal (Linux)

### Prerequisites

- Ubuntu 20.04 / 22.04 or Debian 11+
- Python 3.10+
- Node.js 18+ and npm
- MySQL or MariaDB
- Nginx
- PM2 (`npm install -g pm2`)

### 1. Clone the repository

```bash
git clone https://github.com/dedin7766/rarayvision.git
cd rarayvision
```

### 2. Install Python dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the database

Create the database and user in MySQL:

```sql
CREATE DATABASE rarayvision CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'raray'@'localhost' IDENTIFIED BY 'yourpassword';
GRANT ALL PRIVILEGES ON rarayvision.* TO 'raray'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Configure environment variables

Create `/etc/rarayvision.env` or set environment variables in your shell / PM2 config:

```env
DATABASE_URL=mysql+pymysql://raray:yourpassword@localhost:3306/rarayvision
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### 5. Place ONNX model files

Copy your ONNX model files into `backend/models/`:

```
backend/models/
  best_model_quantized.onnx   — Anti-spoofing model
  emotion-ferplus-8.onnx      — Emotion detection model
```

InsightFace models (buffalo_l) are downloaded automatically on first run into `~/.insightface/models/`.

### 6. Start the backend with PM2

```bash
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

Or manually:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 5000
```

### 7. Build the frontend

```bash
cd frontend
npm install
npm run build
```

The output is in `frontend/dist/`. Serve it via Nginx.

### 8. Configure Nginx

Create `/etc/nginx/sites-available/rarayvision`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend (Vue SPA)
    root /path/to/rarayvision/frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;
        client_max_body_size 20M;
    }

    # Swagger UI and ReDoc
    location ~ ^/(docs|redoc|openapi.json) {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
    }

    # Socket.IO
    location /socket.io/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable and reload:

```bash
ln -s /etc/nginx/sites-available/rarayvision /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 9. Enable HTTPS with Certbot (optional but recommended)

```bash
apt install certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com
```

---

## API Authentication

All face endpoints require a JWT Bearer token in the `Authorization` header:

```
Authorization: Bearer <your-jwt-token>
```

To obtain a token, call the login endpoint:

```bash
curl -X POST https://yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"yourpassword"}'
```

---

## Face Model Notes

- InsightFace downloads the `buffalo_l` model pack automatically on first run. This requires an internet connection during initial startup.
- The anti-spoofing model (`best_model_quantized.onnx`) must be placed manually in `backend/models/`.
- CPU inference is fully supported. GPU (CUDA) is supported if `onnxruntime-gpu` is installed instead of `onnxruntime`.

---

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.

---

## Links

- Live Demo: https://rarayvision.dfs.co.id
- API Base URL: https://apirv.dfs.co.id/api/v1
- Swagger UI: https://apirv.dfs.co.id/docs
- ReDoc: https://apirv.dfs.co.id/redoc 