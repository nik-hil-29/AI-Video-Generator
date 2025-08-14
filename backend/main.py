from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from models.video_generator import VideoGenerator
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Video Generation Full-Stack App", version="1.0.0")

# CORS middleware - allowing all origins since we're serving everything from same domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize video generator
video_generator = VideoGenerator()

class VideoRequest(BaseModel):
    prompt: str
    duration: int = 5

class VideoResponse(BaseModel):
    status: str
    video_url: str = None
    task_id: str = None
    message: str = None

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "AI Video Generation Full-Stack App"}

@app.get("/api")
async def api_root():
    return {"message": "AI Video Generation API", "status": "running", "version": "1.0.0"}

@app.post("/api/generate-video", response_model=VideoResponse)
async def generate_video(request: VideoRequest):
    """Generate a video based on the provided prompt"""
    try:
        logger.info(f"Received video generation request: {request.prompt}")
        
        # Validate prompt
        if not request.prompt or len(request.prompt.strip()) < 3:
            raise HTTPException(status_code=400, detail="Prompt must be at least 3 characters long")
        
        # Generate video using the video generator
        result = await video_generator.generate_video(
            prompt=request.prompt,
            duration=request.duration
        )
        
        if result["status"] == "success":
            return VideoResponse(
                status="success",
                video_url=result["video_url"],
                task_id=result.get("task_id"),
                message="Video generated successfully"
            )
        else:
            return VideoResponse(
                status="processing",
                task_id=result.get("task_id"),
                message="Video generation in progress. Check status with task ID."
            )
            
    except Exception as e:
        logger.error(f"Error generating video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

@app.get("/api/video-status/{task_id}")
async def get_video_status(task_id: str):
    """Check the status of a video generation task"""
    try:
        result = await video_generator.get_generation_status(task_id)
        return result
    except Exception as e:
        logger.error(f"Error checking video status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

# Create static directories
os.makedirs("static/generated_videos", exist_ok=True)

# Mount static files for generated videos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount React build files (if they exist)
if os.path.exists("frontend_build"):
    app.mount("/assets", StaticFiles(directory="frontend_build/assets"), name="assets")
    app.mount("/static", StaticFiles(directory="frontend_build/static"), name="frontend_static")
    
    # Serve React app for all non-API routes
    @app.get("/{path:path}")
    async def serve_react_app(request: Request, path: str):
        """Serve React app for all non-API routes"""
        # Don't serve React for API routes
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        # Serve index.html for all other routes (React Router handles routing)
        return FileResponse("frontend_build/index.html")
    
    @app.get("/")
    async def serve_react_root():
        """Serve React app root"""
        return FileResponse("frontend_build/index.html")
else:
    @app.get("/")
    async def root():
        return {
            "message": "AI Video Generation API", 
            "status": "running",
            "note": "Frontend build not found. Build the React app first."
        }

# Health check for deployment platforms
@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
