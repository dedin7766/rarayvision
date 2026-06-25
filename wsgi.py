import sys
sys.path.insert(0, '/www/wwwroot/rarayvision.dfs.co.id')
from backend.main import app

if __name__ == "__main__":
    from uvicorn import run
    run(app, host="0.0.0.0", port=5000)