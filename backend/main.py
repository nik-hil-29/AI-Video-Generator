from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from models.video_generator import VideoGenerator
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Video Generation API", version="1.0.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for serving generated videos
os.makedirs("static/generated_videos", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize video generator
video_generator = VideoGenerator()

class VideoRequest(BaseModel):
    prompt: str
    duration: int = 5  # Default 5 seconds

class VideoResponse(BaseModel):
    status: str
    video_url: str = None
    task_id: str = None
    message: str = None

@app.get("/")
async def root():
    return {"message": "AI Video Generation API", "status": "running"}

@app.post("/generate-video", response_model=VideoResponse)
async def generate_video(request: VideoRequest):
    """
    Generate a video based on the provided prompt
    """
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

@app.get("/video-status/{task_id}")
async def get_video_status(task_id: str):
    """
    Check the status of a video generation task
    """
    try:
        result = await video_generator.get_generation_status(task_id)
        return result
    except Exception as e:
        logger.error(f"Error checking video status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Video Generation API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)