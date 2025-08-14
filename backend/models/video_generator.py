import os
import asyncio
import uuid
import time
from typing import Dict, Any
import logging
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import base64
import tempfile

load_dotenv()

logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self):
        # Hugging Face API Token
        self.hf_token = os.getenv("HF_TOKEN")
        
        # Initialize Hugging Face client
        self.client = None
        if self.hf_token:
            try:
                self.client = InferenceClient(
                    provider="auto",
                    api_key=self.hf_token,
                )
                logger.info("Hugging Face InferenceClient initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Hugging Face client: {e}")
                self.client = None
        else:
            logger.warning("HF_TOKEN not found, will use mock generation")
        
        # Model configuration
        self.model_name = "Wan-AI/Wan2.2-T2V-A14B"
        
        # Storage for tracking generation tasks
        self.generation_tasks = {}
        
        logger.info("VideoGenerator initialized")
    
    async def generate_video(self, prompt: str, duration: int = 5) -> Dict[str, Any]:
        """
        Generate video using Hugging Face Inference API
        Note: Wan-AI model is fixed at 5 seconds regardless of duration parameter
        """
        task_id = str(uuid.uuid4())
        
        # Force duration to 5 seconds for Wan-AI model
        duration = 5
        
        # Use Hugging Face client or fallback to mock
        if self.client and self.hf_token:
            return await self._generate_with_huggingface(prompt, duration, task_id)
        else:
            # Mock generation for testing without API keys
            return await self._mock_generation(prompt, duration, task_id)
    
    async def _generate_with_huggingface(self, prompt: str, duration: int, task_id: str) -> Dict[str, Any]:
        """
        Generate video using Hugging Face Inference API
        """
        try:
            logger.info(f"Starting Hugging Face video generation with prompt: {prompt}")
            
            # Store task info
            self.generation_tasks[task_id] = {
                "status": "processing",
                "provider": "huggingface",
                "created_at": time.time(),
                "prompt": prompt
            }
            
            # Generate video using Hugging Face client
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            # Calculate frames based on duration (fixed at 5 seconds for Wan-AI)
            # Most video models use 24fps, so for 5 seconds: 5 * 24 = 120 frames
            num_frames = 120  # Fixed for Wan-AI model
            
            logger.info(f"Generating 5-second video with {num_frames} frames using Wan-AI model")
            
            video_result = await loop.run_in_executor(
                None, 
                lambda: self.client.text_to_video(
                    prompt,
                    model=self.model_name,
                    num_frames=num_frames,  # Use frames instead of duration
                    num_inference_steps=25,  # Good quality vs speed balance
                    guidance_scale=7.5,     # Standard guidance scale
                )
            )
            
            # Save the video result
            if video_result:
                # Create filename for the generated video
                video_filename = f"generated_video_{task_id}.mp4"
                video_path = f"static/generated_videos/{video_filename}"
                
                # Ensure directory exists
                os.makedirs("static/generated_videos", exist_ok=True)
                
                # Save video file
                if hasattr(video_result, 'content'):
                    # If video_result has content attribute (bytes)
                    with open(video_path, "wb") as f:
                        f.write(video_result.content)
                elif isinstance(video_result, bytes):
                    # If video_result is bytes directly
                    with open(video_path, "wb") as f:
                        f.write(video_result)
                else:
                    # If video_result is a file-like object or path
                    if hasattr(video_result, 'read'):
                        with open(video_path, "wb") as f:
                            f.write(video_result.read())
                    else:
                        # Assume it's a path or can be copied
                        import shutil
                        shutil.copy(str(video_result), video_path)
                
                # FIXED: Use the correct static path that matches our main.py mounting
                video_url = f"/video-static/generated_videos/{video_filename}"
                
                # Update task status
                self.generation_tasks[task_id].update({
                    "status": "completed",
                    "video_url": video_url
                })
                
                logger.info(f"Video generated successfully: {video_url}")
                
                return {
                    "status": "success",
                    "video_url": video_url,
                    "task_id": task_id,
                    "message": "Video generated successfully using Hugging Face"
                }
            else:
                # Generation failed
                self.generation_tasks[task_id].update({
                    "status": "failed",
                    "error": "No video content received"
                })
                
                return {
                    "status": "error",
                    "message": "Video generation failed - no content received",
                    "task_id": task_id
                }
                
        except Exception as e:
            logger.error(f"Hugging Face generation error: {str(e)}")
            
            # Update task status
            if task_id in self.generation_tasks:
                self.generation_tasks[task_id].update({
                    "status": "failed",
                    "error": str(e)
                })
            
            # Check if it's a model limitation issue
            error_message = str(e)
            if "num_frames" in error_message.lower() or "duration" in error_message.lower():
                error_message = f"Model limitation: The Wan-AI model may only support 5-second videos. Original error: {str(e)}"
            
            return {
                "status": "error",
                "message": f"Hugging Face API error: {error_message}",
                "task_id": task_id
            }
    
    async def _mock_generation(self, prompt: str, duration: int, task_id: str) -> Dict[str, Any]:
        """
        Mock video generation for testing without API keys
        """
        logger.info("Using mock video generation (no HF_TOKEN provided)")
        
        # Simulate processing time
        await asyncio.sleep(3)
        
        # Create a mock video URL that points to a placeholder
        mock_video_url = "/video-static/generated_videos/mock_video.mp4"
        
        self.generation_tasks[task_id] = {
            "status": "completed",
            "video_url": mock_video_url,
            "provider": "mock",
            "created_at": time.time(),
            "prompt": prompt
        }
        
        return {
            "status": "success",
            "video_url": mock_video_url,
            "task_id": task_id,
            "message": "Mock video generated (add HF_TOKEN for real generation)"
        }
    
    async def get_generation_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a generation task
        """
        if task_id not in self.generation_tasks:
            return {"status": "error", "message": "Task not found"}
        
        task_info = self.generation_tasks[task_id]
        
        if task_info["status"] == "completed":
            return {
                "status": "success",
                "video_url": task_info["video_url"],
                "task_id": task_id,
                "message": "Video generation completed"
            }
        elif task_info["status"] == "processing":
            return {
                "status": "processing",
                "task_id": task_id,
                "message": "Video is still being generated..."
            }
        elif task_info["status"] == "failed":
            return {
                "status": "error",
                "task_id": task_id,
                "message": task_info.get("error", "Video generation failed")
            }
        
        return task_info
