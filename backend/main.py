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

# CORS middleware
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

# Debug build structure
def debug_build_structure():
    logger.info("🔍 DEBUGGING BUILD STRUCTURE")
    
    if os.path.exists("frontend_build"):
        for root, dirs, files in os.walk("frontend_build"):
            level = root.replace("frontend_build", "").count(os.sep)
            indent = "  " * level
            logger.info(f"{indent}{os.path.basename(root)}/")
            subindent = "  " * (level + 1)
            for file in files:
                logger.info(f"{subindent}{file}")
        
        # Check index.html content
        index_path = "frontend_build/index.html"
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                content = f.read()
                logger.info("🔍 CSS/JS REFERENCES IN INDEX.HTML:")
                logger.info(content)

debug_build_structure()

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "AI Video Generation Full-Stack App"}

@app.get("/api")
async def api_root():
    return {"message": "AI Video Generation API", "status": "running", "version": "1.0.0"}

@app.post("/api/generate-video", response_model=VideoResponse)
async def generate_video(request: VideoRequest):
    try:
        logger.info(f"Received video generation request: {request.prompt}")
        
        if not request.prompt or len(request.prompt.strip()) < 3:
            raise HTTPException(status_code=400, detail="Prompt must be at least 3 characters long")
        
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
    try:
        result = await video_generator.get_generation_status(task_id)
        return result
    except Exception as e:
        logger.error(f"Error checking video status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

# Create static directories
os.makedirs("static/generated_videos", exist_ok=True)

# FIXED: Mount video static files at a different path to avoid conflicts
app.mount("/video-static", StaticFiles(directory="static"), name="video_static")

# Mount React build files correctly
if os.path.exists("frontend_build"):
    logger.info("Frontend build directory found")
    
    # FIXED: Mount React static directory at /static to match HTML expectations
    react_static_dir = "frontend_build/static"
    if os.path.exists(react_static_dir):
        # This is the key fix - mount at /static to match HTML requests
        app.mount("/static", StaticFiles(directory=react_static_dir), name="react_static")
        logger.info(f"✅ Mounted React static files at /static from {react_static_dir}")
    
    # Serve other React files
    @app.get("/favicon.ico")
    async def favicon():
        favicon_path = "frontend_build/favicon.ico"
        if os.path.exists(favicon_path):
            return FileResponse(favicon_path)
        raise HTTPException(status_code=404)
    
    @app.get("/manifest.json")
    async def manifest():
        manifest_path = "frontend_build/manifest.json"
        if os.path.exists(manifest_path):
            return FileResponse(manifest_path)
        raise HTTPException(status_code=404)
    
    @app.get("/asset-manifest.json")
    async def asset_manifest():
        manifest_path = "frontend_build/asset-manifest.json"
        if os.path.exists(manifest_path):
            return FileResponse(manifest_path)
        raise HTTPException(status_code=404)
    
    # Serve React app for all other routes
    @app.get("/{path:path}")
    async def serve_react_app(path: str):
        """Serve React app for all non-API routes"""
        # Skip API routes and static files
        if (path.startswith("api/") or 
            path.startswith("static/") or 
            path.startswith("video-static/") or
            ("." in path.split("/")[-1] and not path.endswith('.html'))):
            raise HTTPException(status_code=404)
        
        # Serve index.html for React Router
        index_path = "frontend_build/index.html"
        if os.path.exists(index_path):
            return FileResponse(index_path, media_type="text/html")
        else:
            raise HTTPException(status_code=404, detail="Frontend not found")
    
    @app.get("/")
    async def serve_react_root():
        """Serve React app root"""
        index_path = "frontend_build/index.html"
        if os.path.exists(index_path):
            return FileResponse(index_path, media_type="text/html")
        else:
            return {"message": "Frontend build found but index.html missing"}
else:
    logger.warning("Frontend build directory not found")
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
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
