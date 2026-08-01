// import React from "react";

// export default function StatusPanel({ status, connected }) {
//   const landmarks = status?.landmarks;
//   const phone = status?.phone_detection;
//   const components = status?.risk?.components;

//   return (
//     <div>
//       <div className="card" style={{ marginBottom: 20 }}>
//         <h2>Eye &amp; Head Status</h2>
//         <div className="stat-row">
//           <span className="stat-label">Face Detected</span>
//           <span className="stat-value">
//             {landmarks?.face_found ? "✅ Yes" : "❌ No"}
//           </span>
//         </div>
//         <div className="stat-row">
//           <span className="stat-label">Eye Aspect Ratio (EAR)</span>
//           <span className="stat-value">
//             {landmarks?.ear != null ? landmarks.ear.toFixed(3) : "—"}
//           </span>
//         </div>
//         <div className="stat-row">
//           <span className="stat-label">Mouth Aspect Ratio (MAR)</span>
//           <span className="stat-value">
//             {landmarks?.mar != null ? landmarks.mar.toFixed(3) : "—"}
//           </span>
//         </div>
//         <div className="stat-row">
//           <span className="stat-label">Head Yaw</span>
//           <span className="stat-value">
//             {landmarks?.head_pose?.yaw != null
//               ? `${landmarks.head_pose.yaw.toFixed(1)}°`
//               : "—"}
//           </span>
//         </div>
//         <div className="stat-row">
//           <span className="stat-label">Head Pitch</span>
//           <span className="stat-value">
//             {landmarks?.head_pose?.pitch != null
//               ? `${landmarks.head_pose.pitch.toFixed(1)}°`
//               : "—"}
//           </span>
//         </div>
//       </div>

//       <div className="card" style={{ marginBottom: 20 }}>
//         <h2>Phone Detection</h2>
//         <div className="stat-row">
//           <span className="stat-label">Phone Detected</span>
//           <span className="stat-value">
//             {phone?.phone_detected ? "📱 Yes" : "No"}
//           </span>
//         </div>
//         <div className="stat-row">
//           <span className="stat-label">Confidence</span>
//           <span className="stat-value">
//             {phone?.confidence != null ? `${(phone.confidence * 100).toFixed(1)}%` : "—"}
//           </span>
//         </div>
//       </div>

//       <div className="card">
//         <h2>Risk Signal Breakdown</h2>
//         <div className="stat-row">
//           <span className="stat-label">CNN Contribution</span>
//           <span className="stat-value">{components?.cnn_score ?? "—"}</span>
//         </div>
//         <div className="stat-row">
//           <span className="stat-label">Eye Contribution</span>
//           <span className="stat-value">{components?.eye_score ?? "—"}</span>
//         </div>
//         <div className="stat-row">
//           <span className="stat-label">Head Pose Contribution</span>
//           <span className="stat-value">{components?.head_score ?? "—"}</span>
//         </div>
//         <div className="stat-row">
//           <span className="stat-label">Phone Contribution</span>
//           <span className="stat-value">{components?.phone_score ?? "—"}</span>
//         </div>
//         <div className="stat-row">
//           <span className="stat-label">Backend Connection</span>
//           <span className="stat-value">{connected ? "🟢 Online" : "🔴 Offline"}</span>
//         </div>
//       </div>
//     </div>
//   );
// }




import React from "react";

export default function StatusPanel({ status, connected }) {
  const landmarks = status?.landmarks;
  const phone = status?.phone_detection;
  const components = status?.risk?.components;

  return (
    <div>
      <div className="card" style={{ marginBottom: 20 }}>
        <h2>Eye &amp; Head Status</h2>
        <div className="stat-row">
          <span className="stat-label">Face Detected</span>
          <span className="stat-value">
            {landmarks?.face_found ? "✅ Yes" : "❌ No"}
          </span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Eye Aspect Ratio (EAR)</span>
          <span className="stat-value">
            {landmarks?.ear != null ? landmarks.ear.toFixed(3) : "—"}
          </span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Mouth Aspect Ratio (MAR)</span>
          <span className="stat-value">
            {landmarks?.mar != null ? landmarks.mar.toFixed(3) : "—"}
          </span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Head Yaw</span>
          <span className="stat-value">
            {landmarks?.head_pose?.yaw != null
              ? `${landmarks.head_pose.yaw.toFixed(1)}°`
              : "—"}
          </span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Head Pitch</span>
          <span className="stat-value">
            {landmarks?.head_pose?.pitch != null
              ? `${landmarks.head_pose.pitch.toFixed(1)}°`
              : "—"}
          </span>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <h2>Phone Detection</h2>
        <div className="stat-row">
          <span className="stat-label">Phone Detected</span>
          <span className="stat-value">
            {phone?.phone_detected ? "📱 Yes" : "No"}
          </span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Confidence</span>
          <span className="stat-value">
            {phone?.confidence != null ? `${(phone.confidence * 100).toFixed(1)}%` : "—"}
          </span>
        </div>
      </div>

      <div className="card">
        <h2>Risk Signal Breakdown</h2>
        <div className="stat-row">
          <span className="stat-label">CNN Contribution</span>
          <span className="stat-value">{components?.cnn_score ?? "—"}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Eye Contribution</span>
          <span className="stat-value">{components?.eye_score ?? "—"}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Head Pose Contribution</span>
          <span className="stat-value">{components?.head_score ?? "—"}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Phone Contribution</span>
          <span className="stat-value">{components?.phone_score ?? "—"}</span>
        </div>
        <div className="stat-row">
          <span className="stat-label">Backend Connection</span>
          <span className="stat-value">{connected ? "🟢 Online" : "🔴 Offline"}</span>
        </div>
      </div>
    </div>
  );
}