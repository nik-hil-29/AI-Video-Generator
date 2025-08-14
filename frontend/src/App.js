import React from 'react';
import './App.css';
import VideoGenerator from './components/VideoGenerator';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>🎬 AI Video Generator</h1>
        <p>Create amazing videos from text prompts using AI</p>
      </header>
      
      <main className="App-main">
        <VideoGenerator />
      </main>
      
      <footer className="App-footer">
        <p>Powered by AI | Built with React & FastAPI</p>
      </footer>
    </div>
  );
}

export default App;