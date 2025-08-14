from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
import uuid
import time
from typing import Dict, Any
import logging
from huggingface_hub import InferenceClient
import tempfile
import base64

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Video Generation API", version="1.0.0")

# CORS middleware - allow all origins for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize video generator (stateless for Vercel)
class VideoRequest(BaseModel):
    prompt: str
    duration: int = 5

class VideoResponse(BaseModel):
    status: str
    video_url: str = None
    video_data: str = None  # Base64 encoded video for serverless
    task_id: str = None
    message: str = None

# Stateless video generation for Vercel
async def generate_video_serverless(prompt: str, duration: int) -> Dict[str, Any]:
    """Generate video in stateless serverless environment"""
    task_id = str(uuid.uuid4())
    
    try:
        # Get HF token from environment
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            return {
                "status": "error",
                "message": "HF_TOKEN not configured",
                "task_id": task_id
            }
        
        logger.info(f"Starting serverless video generation: {prompt}")
        
        # Create HF client
        client = InferenceClient(api_key=hf_token)
        
        # Generate video with shorter timeout for serverless
        try:
            video_result = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: client.text_to_video(
                        prompt,
                        model="Wan-AI/Wan2.2-T2V-A14B",
                    )
                ),
                timeout=240  # 4 minute timeout for Vercel Pro
            )
        except asyncio.TimeoutError:
            return {
                "status": "error",
                "message": "Video generation timed out. Try a shorter/simpler prompt.",
                "task_id": task_id
            }
        
        logger.info(f"Video generation completed, type: {type(video_result)}")
        
        if video_result:
            # Handle different response types and convert to base64
            video_data = None
            
            if hasattr(video_result, 'content'):
                video_data = video_result.content
            elif isinstance(video_result, bytes):
                video_data = video_result
            elif hasattr(video_result, 'read'):
                video_data = video_result.read()
            elif isinstance(video_result, str) and os.path.exists(video_result):
                with open(video_result, 'rb') as f:
                    video_data = f.read()
            
            if video_data:
                # Convert to base64 for transmission
                video_base64 = base64.b64encode(video_data).decode('utf-8')
                
                logger.info(f"Video encoded successfully, size: {len(video_data)} bytes")
                
                return {
                    "status": "success",
                    "video_data": video_base64,
                    "task_id": task_id,
                    "message": "Video generated successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": "No video content received from AI model",
                    "task_id": task_id
                }
        else:
            return {
                "status": "error",
                "message": "No result from AI model",
                "task_id": task_id
            }
            
    except Exception as e:
        logger.error(f"Serverless generation error: {str(e)}")
        return {
            "status": "error",
            "message": f"Generation failed: {str(e)}",
            "task_id": task_id
        }

@app.get("/")
async def root():
    return {"message": "AI Video Generation API (Serverless)", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Video Generation API (Serverless)"}

@app.post("/generate-video", response_model=VideoResponse)
async def generate_video(request: VideoRequest):
    """Generate a video based on the provided prompt (serverless)"""
    try:
        logger.info(f"Received serverless video generation request: {request.prompt}")
        
        # Validate prompt
        if not request.prompt or len(request.prompt.strip()) < 3:
            raise HTTPException(status_code=400, detail="Prompt must be at least 3 characters long")
        
        # Generate video
        result = await generate_video_serverless(
            prompt=request.prompt,
            duration=request.duration
        )
        
        if result["status"] == "success":
            return VideoResponse(
                status="success",
                video_data=result["video_data"],
                task_id=result["task_id"],
                message="Video generated successfully (serverless)"
            )
        else:
            return VideoResponse(
                status="error",
                task_id=result["task_id"],
                message=result["message"]
            )
            
    except Exception as e:
        logger.error(f"Error in serverless generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Video generation failed: {str(e)}")

# For Vercel deployment
handler = app