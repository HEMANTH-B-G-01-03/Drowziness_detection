// import React, { useRef, useEffect, useState } from "react";
// import { API_BASE_URL } from "../App";

// /**
//  * VideoFeed supports two capture modes:
//  *  - "server": the Flask backend opens the webcam itself (cv2.VideoCapture)
//  *      and streams processed frames back via the /video_feed MJPEG endpoint.
//  *      Use the "Start Server Capture" button in App.js for this mode.
//  *  - "browser": the browser captures webcam frames via getUserMedia and
//  *      posts them to /api/analyze_frame for inference. Useful when the
//  *      backend has no camera attached (e.g., running in the cloud) but the
//  *      user's laptop does.
//  */
// export default function VideoFeed({ onFrameCaptured, captureMode, setCaptureMode }) {
//   const videoRef = useRef(null);
//   const canvasRef = useRef(null);
//   const streamRef = useRef(null);
//   const [browserActive, setBrowserActive] = useState(false);

//   useEffect(() => {
//     if (captureMode !== "browser") {
//       stopBrowserCapture();
//       return;
//     }

//     let intervalId;

//     async function startBrowserCapture() {
//       try {
//         const stream = await navigator.mediaDevices.getUserMedia({ video: true });
//         streamRef.current = stream;
//         if (videoRef.current) {
//           videoRef.current.srcObject = stream;
//           await videoRef.current.play();
//         }
//         setBrowserActive(true);

//         intervalId = setInterval(() => {
//           captureAndSend();
//         }, 500);
//       } catch (err) {
//         console.error("Could not access webcam:", err);
//         setBrowserActive(false);
//       }
//     }

//     startBrowserCapture();

//     return () => {
//       clearInterval(intervalId);
//       stopBrowserCapture();
//     };
//     // eslint-disable-next-line react-hooks/exhaustive-deps
//   }, [captureMode]);

//   function stopBrowserCapture() {
//     if (streamRef.current) {
//       streamRef.current.getTracks().forEach((track) => track.stop());
//       streamRef.current = null;
//     }
//     setBrowserActive(false);
//   }

//   function captureAndSend() {
//     const video = videoRef.current;
//     const canvas = canvasRef.current;
//     if (!video || !canvas || video.readyState !== 4) return;

//     canvas.width = video.videoWidth;
//     canvas.height = video.videoHeight;
//     const ctx = canvas.getContext("2d");
//     ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
//     const base64Image = canvas.toDataURL("image/jpeg", 0.7);
//     onFrameCaptured(base64Image);
//   }

//   return (
//     <div>
//       <div className="video-wrapper">
//         {captureMode === "server" ? (
//           <img src={`${API_BASE_URL}/video_feed`} alt="Live driver camera feed" />
//         ) : (
//           <video ref={videoRef} muted playsInline />
//         )}
//       </div>
//       <canvas ref={canvasRef} style={{ display: "none" }} />

//       <div className="controls">
//         <button
//           onClick={() => setCaptureMode("server")}
//           style={{
//             background: captureMode === "server" ? "#38bdf8" : "#1f2937",
//             color: captureMode === "server" ? "#0b1120" : "#e5e7eb",
//           }}
//         >
//           Server Webcam
//         </button>
//         <button
//           onClick={() => setCaptureMode("browser")}
//           style={{
//             background: captureMode === "browser" ? "#38bdf8" : "#1f2937",
//             color: captureMode === "browser" ? "#0b1120" : "#e5e7eb",
//           }}
//         >
//           Browser Webcam {browserActive ? "(active)" : ""}
//         </button>
//       </div>
//     </div>
//   );
// }


import React, { useRef, useEffect, useState } from "react";
import { API_BASE_URL } from "../App";

/**
 * VideoFeed supports two capture modes:
 *  - "server": the Flask backend opens the webcam itself (cv2.VideoCapture)
 *      and streams processed frames back via the /video_feed MJPEG endpoint.
 *      Use the "Start Server Capture" button in App.js for this mode.
 *  - "browser": the browser captures webcam frames via getUserMedia and
 *      posts them to /api/analyze_frame for inference. Useful when the
 *      backend has no camera attached (e.g., running in the cloud) but the
 *      user's laptop does.
 */
export default function VideoFeed({ onFrameCaptured, captureMode, setCaptureMode }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const [browserActive, setBrowserActive] = useState(false);

  useEffect(() => {
    if (captureMode !== "browser") {
      stopBrowserCapture();
      return;
    }

    let intervalId;

    async function startBrowserCapture() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        streamRef.current = stream;
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          await videoRef.current.play();
        }
        setBrowserActive(true);

        intervalId = setInterval(() => {
          captureAndSend();
        }, 500);
      } catch (err) {
        console.error("Could not access webcam:", err);
        setBrowserActive(false);
      }
    }

    startBrowserCapture();

    return () => {
      clearInterval(intervalId);
      stopBrowserCapture();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [captureMode]);

  function stopBrowserCapture() {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setBrowserActive(false);
  }

  function captureAndSend() {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.readyState !== 4) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    const base64Image = canvas.toDataURL("image/jpeg", 0.7);
    onFrameCaptured(base64Image);
  }

  return (
    <div>
      <div className="video-wrapper">
        {captureMode === "server" ? (
          <img src={`${API_BASE_URL}/video_feed`} alt="Live driver camera feed" />
        ) : (
          <video ref={videoRef} muted playsInline />
        )}
      </div>
      <canvas ref={canvasRef} style={{ display: "none" }} />

      <div className="controls">
        <button
          onClick={() => setCaptureMode("server")}
          style={{
            background: captureMode === "server" ? "#38bdf8" : "#1f2937",
            color: captureMode === "server" ? "#0b1120" : "#e5e7eb",
          }}
        >
          Server Webcam
        </button>
        <button
          onClick={() => setCaptureMode("browser")}
          style={{
            background: captureMode === "browser" ? "#38bdf8" : "#1f2937",
            color: captureMode === "browser" ? "#0b1120" : "#e5e7eb",
          }}
        >
          Browser Webcam {browserActive ? "(active)" : ""}
        </button>
      </div>
    </div>
  );
}