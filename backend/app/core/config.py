import os

# JWT Configuration
SECRET_KEY = "RARAYVISION_SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days

# Base paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Model paths (inside backend/models/)
ANTI_SPOOF_MODEL_PATH = os.path.join(BASE_DIR, "models", "MiniFASNetV2.onnx")
EMOTION_MODEL_PATH = os.path.join(BASE_DIR, "models", "emotion-ferplus-8.onnx")

# External Services
CI_BASE_URL = "https://yourdomain.com/Api_user"
