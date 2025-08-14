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

# Mount React build files (if they exist) - Check directories first
if os.path.exists("frontend_build"):
    logger.info("Frontend build directory found")
    
    # Mount React static files (only if they exist)
    react_static_dir = "frontend_build/static"
    if os.path.exists(react_static_dir):
        app.mount("/static-react", StaticFiles(directory=react_static_dir), name="frontend_static")
        logger.info(f"Mounted React static files from {react_static_dir}")
    
    # Mount React assets (only if they exist)
    react_assets_dir = "frontend_build/assets"  
    if os.path.exists(react_assets_dir):
        app.mount("/assets", StaticFiles(directory=react_assets_dir), name="assets")
        logger.info(f"Mounted React assets from {react_assets_dir}")
    
    # List what's actually in the frontend_build directory
    try:
        build_contents = os.listdir("frontend_build")
        logger.info(f"Frontend build contents: {build_contents}")
    except Exception as e:
        logger.error(f"Could not list frontend_build contents: {e}")
    
    # Serve React app for all non-API routes
    @app.get("/{path:path}")
    async def serve_react_app(request: Request, path: str):
        """Serve React app for all non-API routes"""
        # Don't serve React for API routes or static files
        if path.startswith("api/") or path.startswith("static"):
            raise HTTPException(status_code=404, detail="Not found")
        
        # Check if it's a static file request
        if "." in path.split("/")[-1]:
            # Try to serve from frontend_build directly
            file_path = os.path.join("frontend_build", path)
            if os.path.exists(file_path):
                return FileResponse(file_path)
        
        # Serve index.html for all other routes (React Router handles routing)
        index_path = "frontend_build/index.html"
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")
    
    @app.get("/")
    async def serve_react_root():
        """Serve React app root"""
        index_path = "frontend_build/index.html"
        if os.path.exists(index_path):
            return FileResponse(index_path)
        else:
            return {"message": "Frontend build found but index.html missing"}
else:
    logger.warning("Frontend build directory not found")
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
