import React, { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import Dashboard from "./components/Dashboard";
import VideoFeed from "./components/VideoFeed";
import StatusPanel from "./components/StatusPanel";

export const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

function App() {
  const [status, setStatus] = useState(null);
  const [connected, setConnected] = useState(false);
  const [captureMode, setCaptureMode] = useState("server"); // "server" or "browser"
  const pollRef = useRef(null);

  const fetchStatus = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/api/status`);
      setStatus(res.data);
      setConnected(true);
    } catch (err) {
      setConnected(false);
    }
  }, []);

  useEffect(() => {
    // Poll backend /api/status every 500ms for the latest inference results
    pollRef.current = setInterval(fetchStatus, 500);
    fetchStatus();
    return () => clearInterval(pollRef.current);
  }, [fetchStatus]);

  const handleStart = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/start`, { source: 0 });
    } catch (err) {
      console.error("Failed to start capture", err);
    }
  };

  const handleStop = async () => {
    try {
      await axios.post(`${API_BASE_URL}/api/stop`);
    } catch (err) {
      console.error("Failed to stop capture", err);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🚗 Advanced Driver Vigilance System</h1>
        <p>
          <span className={`connection-dot ${connected ? "dot-online" : "dot-offline"}`}></span>
          {connected ? "Connected to backend" : "Backend offline — start app.py"}
        </p>
      </header>

      <div className="dashboard-grid">
        <div>
          <div className="card" style={{ marginBottom: 20 }}>
            <h2>Live Camera Feed</h2>
            <VideoFeed
              status={status}
              onFrameCaptured={async (base64Image) => {
                try {
                  const res = await axios.post(`${API_BASE_URL}/api/analyze_frame`, {
                    image: base64Image,
                  });
                  setStatus(res.data);
                  setConnected(true);
                } catch (err) {
                  setConnected(false);
                }
              }}
              captureMode={captureMode}
              setCaptureMode={setCaptureMode}
            />
            <div className="controls">
              <button className="btn-start" onClick={handleStart}>
                ▶ Start Server Capture
              </button>
              <button className="btn-stop" onClick={handleStop}>
                ⏸ Stop Server Capture
              </button>
            </div>
          </div>
          <Dashboard status={status} />
        </div>

        <StatusPanel status={status} connected={connected} />
      </div>
    </div>
  );
}

export default App;