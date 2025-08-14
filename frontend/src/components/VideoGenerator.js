import React, { useState } from 'react';
import axios from 'axios';

const VideoGenerator = () => {
  const [prompt, setPrompt] = useState('');
  const [duration, setDuration] = useState(5);
  const [isGenerating, setIsGenerating] = useState(false);
  const [status, setStatus] = useState('');
  const [videoUrl, setVideoUrl] = useState('');
  const [taskId, setTaskId] = useState('');
  const [error, setError] = useState('');

  // API base URL
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  const handleGenerateVideo = async () => {
    // Validation
    if (!prompt.trim()) {
      setError('Please enter a prompt for video generation');
      return;
    }

    if (prompt.trim().length < 3) {
      setError('Prompt must be at least 3 characters long');
      return;
    }

    setIsGenerating(true);
    setError('');
    setVideoUrl('');
    setStatus('Generating video...');

    try {
      const response = await axios.post(`${API_BASE_URL}/generate-video`, {
        prompt: prompt.trim(),
        duration: parseInt(duration)
      }, {
        timeout: 120000 // 2 minute timeout
      });

      const data = response.data;

      if (data.status === 'success') {
        setVideoUrl(data.video_url);
        setStatus('Video generated successfully!');
        setTaskId(data.task_id || '');
      } else if (data.status === 'processing') {
        setTaskId(data.task_id);
        setStatus('Video generation in progress...');
        // Start polling for status updates
        pollVideoStatus(data.task_id);
      } else {
        setError(data.message || 'Unknown error occurred');
        setStatus('');
      }
    } catch (err) {
      console.error('Video generation error:', err);
      
      if (err.code === 'ECONNABORTED') {
        setError('Request timeout - video generation is taking longer than expected');
      } else if (err.response) {
        setError(err.response.data?.detail || 'Server error occurred');
      } else if (err.request) {
        setError('Unable to connect to server. Please check if the backend is running.');
      } else {
        setError('An unexpected error occurred');
      }
      setStatus('');
    } finally {
      setIsGenerating(false);
    }
  };

  const pollVideoStatus = async (taskId) => {
    const maxPolls = 30; // Max 5 minutes of polling (10 second intervals)
    let pollCount = 0;

    const poll = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/video-status/${taskId}`);
        const data = response.data;

        if (data.status === 'success') {
          setVideoUrl(data.video_url);
          setStatus('Video generated successfully!');
          setIsGenerating(false);
        } else if (data.status === 'processing') {
          pollCount++;
          if (pollCount < maxPolls) {
            setStatus(`Video generation in progress... (${pollCount}/${maxPolls})`);
            setTimeout(poll, 10000); // Poll every 10 seconds
          } else {
            setError('Video generation is taking longer than expected. Please try again.');
            setStatus('');
            setIsGenerating(false);
          }
        } else {
          setError(data.message || 'Video generation failed');
          setStatus('');
          setIsGenerating(false);
        }
      } catch (err) {
        console.error('Status polling error:', err);
        setError('Failed to check video generation status');
        setStatus('');
        setIsGenerating(false);
      }
    };

    poll();
  };

  const handleDownloadVideo = () => {
    if (videoUrl) {
      const link = document.createElement('a');
      link.href = videoUrl;
      link.download = `generated-video-${Date.now()}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const resetForm = () => {
    setPrompt('');
    setDuration(5);
    setVideoUrl('');
    setStatus('');
    setError('');
    setTaskId('');
    setIsGenerating(false);
  };

  return (
    <div className="video-generator">
      <div className="generator-header">
        <h2>✨ Generate Your Video</h2>
        <p>Describe what you want to see and let AI create it for you</p>
      </div>

      <div className="generator-content">
        {/* Input Section */}
        <div className="input-section">
          <div className="input-group">
            <label htmlFor="prompt">Video Prompt *</label>
            <textarea
              id="prompt"
              className="prompt-input"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g., A serene sunset over a calm ocean with gentle waves..."
              disabled={isGenerating}
              maxLength={500}
            />
            <small style={{ color: '#666', fontSize: '0.8rem' }}>
              {prompt.length}/500 characters
            </small>
          </div>

          <div className="input-group">
            <label htmlFor="duration">Duration (seconds)</label>
            <input
              id="duration"
              type="number"
              className="duration-input"
              value={duration}
              onChange={(e) => setDuration(e.target.value)}
              min="3"
              max="10"
              disabled={isGenerating}
            />
            <small style={{ color: '#666', fontSize: '0.8rem', marginLeft: '0.5rem' }}>
              3-10 seconds
            </small>
          </div>

          <button
            className="generate-button"
            onClick={handleGenerateVideo}
            disabled={isGenerating || !prompt.trim()}
          >
            {isGenerating ? (
              <>
                <span className="loading-spinner"></span>
                Generating...
              </>
            ) : (
              '🎬 Generate Video'
            )}
          </button>

          {videoUrl && (
            <button
              className="generate-button"
              onClick={resetForm}
              style={{ marginLeft: '1rem', background: '#6c757d' }}
            >
              Generate New Video
            </button>
          )}
        </div>

        {/* Status Section */}
        {(status || error) && (
          <div className={`status-section ${error ? 'status-error' : isGenerating ? 'status-processing' : 'status-success'}`}>
            {error ? (
              <div className="error-message">
                <strong>❌ Error:</strong> {error}
              </div>
            ) : (
              <div>
                {isGenerating && <span className="loading-spinner"></span>}
                <strong>ℹ️ Status:</strong> {status}
                {taskId && (
                  <div style={{ fontSize: '0.8rem', marginTop: '0.5rem', opacity: 0.8 }}>
                    Task ID: {taskId}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Video Display Section */}
        {videoUrl && (
          <div className="video-section">
            <div className="video-container">
              <video
                className="video-player"
                controls
                autoPlay
                muted
                loop
                src={videoUrl}
                onError={(e) => {
                  console.error('Video playback error:', e);
                  setError('Failed to load generated video');
                }}
              >
                Your browser does not support the video tag.
              </video>
            </div>

            <div className="video-info">
              <h3>🎉 Video Generated Successfully!</h3>
              <p><strong>Prompt:</strong> {prompt}</p>
              <p><strong>Duration:</strong> {duration} seconds</p>
              <p><strong>Generated at:</strong> {new Date().toLocaleString()}</p>
              
              {videoUrl.startsWith('http') && (
                <button 
                  className="download-button"
                  onClick={handleDownloadVideo}
                >
                  📥 Download Video
                </button>
              )}
            </div>
          </div>
        )}

        {/* Help Section */}
        <div style={{ marginTop: '2rem', padding: '1rem', background: '#f8f9fa', borderRadius: '8px' }}>
          <h4 style={{ margin: '0 0 1rem 0', color: '#333' }}>💡 Tips for better videos:</h4>
          <ul style={{ textAlign: 'left', color: '#666', margin: 0 }}>
            <li>Be descriptive and specific in your prompts</li>
            <li>Include details about lighting, movement, and style</li>
            <li>Try phrases like "cinematic", "slow motion", or "aerial view"</li>
            <li>Shorter videos (3-5 seconds) generate faster</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default VideoGenerator;