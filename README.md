# 🎬 AI Video Generator

A full-stack web application that generates high-quality videos from text prompts using the powerful Wan-AI/Wan2.2-T2V-A14B model.

## 🌟 Live Demo

**Try it now:** [https://ai-video-generator-uwq8.onrender.com](https://ai-video-generator-uwq8.onrender.com)

## ✨ Features

- **Text-to-Video Generation**: Create 5-second, 720P videos from descriptive text prompts
- **High-Quality Output**: 24fps videos with excellent visual fidelity
- **Real-time Status Updates**: Track video generation progress with live polling
- **Responsive Design**: Beautiful, mobile-friendly interface
- **Download Videos**: Save generated videos directly to your device
- **Error Handling**: Comprehensive error messages and user guidance

## 🛠️ Technology Stack

### Frontend
- **React 18** - Modern UI library
- **Axios** - HTTP client for API requests
- **CSS3** - Custom styling with gradients and animations
- **Responsive Design** - Works on desktop and mobile

### Backend
- **FastAPI** - High-performance Python web framework
- **Hugging Face Hub** - AI model inference
- **Uvicorn** - ASGI server for production
- **Python 3.11** - Core backend language

### AI Model
- **Wan-AI/Wan2.2-T2V-A14B** - State-of-the-art text-to-video model
- **Mixture-of-Experts (MoE)** architecture with 27B total parameters
- **Optimized for 5-second videos** at 720P resolution

### Deployment
- **Render** - Cloud hosting platform
- **Docker** - Containerized deployment
- **Multi-stage builds** - Optimized container images

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- Hugging Face account and API token

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-video-generator.git
   cd ai-video-generator
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Create .env file
   echo "HF_TOKEN=your_huggingface_token_here" > .env
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

4. **Run the application**
   ```bash
   cd backend
   python main.py
   ```

5. **Access the app**
   Open [http://localhost:8000](http://localhost:8000) in your browser

## 🔧 Environment Variables

Create a `.env` file in the `backend` directory:

```bash
HF_TOKEN=your_huggingface_token_here
PORT=8000
ENVIRONMENT=development
```

## 📋 API Endpoints

### Generate Video
```http
POST /api/generate-video
Content-Type: application/json

{
  "prompt": "A serene sunset over calm ocean waves",
  "duration": 5
}
```

### Check Video Status
```http
GET /api/video-status/{task_id}
```

### Health Check
```http
GET /health
```

## ⚠️ Known Limitations

### Hugging Face Free Tier Limits
- **Limited Usage**: The free Hugging Face Inference API has usage limits
- **Rate Limiting**: After 3-4 video generations, you may encounter "free tier exhausted" errors
- **Cool-down Period**: Free tier resets after some time

### Solutions for Production Use

1. **Upgrade to Hugging Face Pro** ($20/month)
   - Higher rate limits
   - Faster inference
   - Priority access

2. **Local Model Deployment** (Recommended for heavy usage)
   ```bash
   # Download model locally (requires ~50GB storage)
   huggingface-cli download Wan-AI/Wan2.2-T2V-A14B --local-dir ./models/
   
   # Deploy on paid cloud with GPU support:
   # - AWS EC2 with GPU instances
   # - Google Cloud Platform with TPUs
   # - Azure GPU VMs
   # - RunPod, Paperspace, or Lambda Labs
   ```

3. **Self-hosted Infrastructure**
   - Requires NVIDIA GPU with 16GB+ VRAM
   - Ubuntu/Linux server with CUDA support
   - Docker deployment with GPU access

## 🐳 Docker Deployment

### Build and run locally
```bash
docker build -t ai-video-generator .
docker run -p 8000:8000 -e HF_TOKEN=your_token ai-video-generator
```

### Deploy to Render
1. Connect your GitHub repository to Render
2. Set environment variable `HF_TOKEN` in Render dashboard
3. Deploy using the included `render.yaml` configuration

## 💡 Usage Tips

### Writing Better Prompts
- **Be specific and descriptive**: "A majestic lion walking through African savanna at golden hour"
- **Include style details**: "cinematic lighting", "slow motion", "aerial view"
- **Mention camera angles**: "close-up", "wide shot", "tracking shot"
- **Describe movement**: "gentle waves", "flowing fabric", "rotating object"

### Prompt Examples
```
• "A hummingbird hovering near vibrant red flowers in slow motion"
• "Cinematic shot of rain drops falling on a window at sunset"
• "A paper airplane gliding through a sunny classroom"
• "Ocean waves crashing against rocky cliffs with dramatic lighting"
• "A cat stretching and yawning on a cozy windowsill"
```

## 🔮 Future Enhancements

- [ ] Support for longer video durations
- [ ] Multiple video resolution options
- [ ] Batch video generation
- [ ] Video style transfer
- [ ] Integration with additional AI models
- [ ] User accounts and video history
- [ ] Video editing capabilities
- [ ] Social sharing features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Wan-AI Team** for the incredible Wan2.2-T2V-A14B model
- **Hugging Face** for the inference infrastructure
- **Render** for the hosting platform
- **OpenAI** for inspiration in AI applications

## 📞 Support

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/your-username/ai-video-generator/issues)
- **Discussions**: Join conversations in [GitHub Discussions](https://github.com/your-username/ai-video-generator/discussions)
- **Email**: contact@your-domain.com

## 📊 Project Stats

- **Model Size**: 27B parameters (14B active)
- **Video Quality**: 720P @ 24fps
- **Video Length**: 5 seconds (optimized)
- **Deployment**: Dockerized on Render
- **Tech Stack**: React + FastAPI + Hugging Face

---

**Made with ❤️ for the AI community**

*Star ⭐ this repo if you found it helpful!*
