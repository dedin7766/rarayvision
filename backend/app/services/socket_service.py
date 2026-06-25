import socketio
import base64
import asyncio

from backend.app.services.ml_service import process_image_sync, thread_pool

# Setup Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")

@sio.event
async def connect(sid, environ):
    print(f"Socket connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Socket disconnected: {sid}")

@sio.event
async def analyze_frame(sid, data):
    try:
        if "image" not in data:
            return
        
        image_data = data["image"]
        
        # Pisahkan header data URI jika ada (misal: "data:image/jpeg;base64,...")
        if "," in image_data:
            image_data = image_data.split(",")[1]
            
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            thread_pool,
            process_image_sync,
            image_data
        )
        
        await sio.emit('analysis_result', result, to=sid)
        
    except Exception as e:
        print(f"Error in analyze_frame: {e}")
        await sio.emit('analysis_error', {"error": str(e)}, to=sid)
