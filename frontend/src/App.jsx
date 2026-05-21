
// import {
//   FaExclamationTriangle,
//   FaPhone,
//   FaEye,
//   FaCarCrash,
// } from "react-icons/fa";

// function App() {
//   return (
//     <div className="min-h-screen bg-slate-950 text-white p-6">

//       {/* HEADER */}
//       <div className="flex justify-between items-center mb-8">

//         <div>
//           <h1 className="text-4xl font-bold text-cyan-400">
//             AI Driver Monitoring System
//           </h1>

//           <p className="text-gray-400 mt-2">
//             Real-Time Drowsiness & Distraction Detection
//           </p>
//         </div>

//         <div className="bg-red-500 px-5 py-3 rounded-xl shadow-lg font-bold text-lg animate-pulse">
//           HIGH RISK
//         </div>

//       </div>

//       {/* MAIN GRID */}
//       <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

//         {/* CAMERA SECTION */}
//         <div className="lg:col-span-2 bg-slate-900 rounded-2xl p-4 border border-slate-800 shadow-2xl">

//           <h2 className="text-2xl font-semibold mb-4 text-cyan-300">
//             Live Monitoring
//           </h2>

//           <div className="w-full h-[500px] rounded-2xl bg-black border border-cyan-500 flex items-center justify-center">

//             <p className="text-gray-500 text-xl">
//               Camera Feed Will Appear Here
//             </p>

//           </div>

//         </div>

//         {/* RIGHT SIDE */}
//         <div className="space-y-6">

//           {/* ALERT CARD */}
//           <div className="bg-slate-900 p-5 rounded-2xl border border-red-500 shadow-xl">

//             <div className="flex items-center gap-3 mb-3">

//               <FaExclamationTriangle className="text-red-500 text-2xl" />

//               <h2 className="text-xl font-bold">
//                 Current Alert
//               </h2>

//             </div>

//             <p className="text-red-400 text-lg">
//               Driver Using Phone
//             </p>

//           </div>

//           {/* RISK SCORE */}
//           <div className="bg-slate-900 p-5 rounded-2xl border border-yellow-500 shadow-xl">

//             <h2 className="text-xl font-bold mb-4">
//               Risk Score
//             </h2>

//             <div className="w-full bg-slate-700 rounded-full h-6 overflow-hidden">

//               <div className="bg-yellow-400 h-6 w-[75%]"></div>

//             </div>

//             <p className="mt-3 text-yellow-300 font-semibold">
//               75% Risk Detected
//             </p>

//           </div>

//           {/* STATUS CARDS */}
//           <div className="grid grid-cols-1 gap-4">

//             {/* EYE STATUS */}
//             <div className="bg-slate-900 p-4 rounded-2xl border border-cyan-500 flex items-center gap-4 shadow-lg">

//               <FaEye className="text-cyan-400 text-3xl" />

//               <div>
//                 <p className="text-gray-400">
//                   Eye Status
//                 </p>

//                 <h3 className="text-xl font-bold text-cyan-300">
//                   Drowsy
//                 </h3>
//               </div>

//             </div>

//             {/* PHONE STATUS */}
//             <div className="bg-slate-900 p-4 rounded-2xl border border-purple-500 flex items-center gap-4 shadow-lg">

//               <FaPhone className="text-purple-400 text-3xl" />

//               <div>
//                 <p className="text-gray-400">
//                   Phone Usage
//                 </p>

//                 <h3 className="text-xl font-bold text-purple-300">
//                   Detected
//                 </h3>
//               </div>

//             </div>

//             {/* ACCURACY */}
//             <div className="bg-slate-900 p-4 rounded-2xl border border-green-500 flex items-center gap-4 shadow-lg">

//               <FaCarCrash className="text-green-400 text-3xl" />

//               <div>
//                 <p className="text-gray-400">
//                   Model Accuracy
//                 </p>

//                 <h3 className="text-xl font-bold text-green-300">
//                   99.94%
//                 </h3>
//               </div>

//             </div>

//           </div>

//         </div>

//       </div>

//     </div>
//   );
// }

// export default App;




import {
  FaExclamationTriangle,
  FaPhone,
  FaEye,
  FaCarCrash,
} from "react-icons/fa";

function App() {
  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">

      {/* HEADER */}
      <div className="flex justify-between items-center mb-8">

        <div>
          <h1 className="text-5xl font-bold text-cyan-400">
            AI Driver Monitoring System
          </h1>

          <p className="text-gray-400 mt-3 text-lg">
            Real-Time Drowsiness & Distraction Detection
          </p>
        </div>

        <div className="bg-red-500 px-5 py-3 rounded-2xl shadow-2xl font-bold text-lg animate-pulse">
          HIGH RISK
        </div>

      </div>

      {/* GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* CAMERA */}
        <div className="lg:col-span-2 bg-slate-900 rounded-3xl p-5 border border-cyan-500 shadow-2xl">

          <h2 className="text-3xl font-bold text-cyan-300 mb-5">
            Live Monitoring
          </h2>

          <div className="h-[500px] rounded-3xl bg-black border-2 border-cyan-400 flex items-center justify-center">

            {/* <p className="text-gray-500 text-2xl">
              Camera Feed Will Appear Here
            </p> */}


        
<img
  src="http://127.0.0.1:5000/video_feed"
  alt="Live Feed"
  className="w-full h-full object-cover rounded-3xl"
/>


          </div>

        </div>

        {/* RIGHT PANEL */}
        <div className="space-y-6">

          {/* ALERT */}
          <div className="bg-slate-900 rounded-3xl p-5 border border-red-500 shadow-2xl">

            <div className="flex items-center gap-3 mb-4">

              <FaExclamationTriangle className="text-red-500 text-3xl" />

              <h2 className="text-2xl font-bold">
                Current Alert
              </h2>

            </div>

            <p className="text-red-400 text-xl">
              Driver Using Phone
            </p>

          </div>

          {/* RISK */}
          <div className="bg-slate-900 rounded-3xl p-5 border border-yellow-500 shadow-2xl">

            <h2 className="text-2xl font-bold mb-4">
              Risk Score
            </h2>

            <div className="w-full h-6 bg-slate-700 rounded-full overflow-hidden">

              <div className="h-6 w-[75%] bg-yellow-400 rounded-full"></div>

            </div>

            <p className="mt-4 text-yellow-300 text-lg font-semibold">
              75% Risk Detected
            </p>

          </div>

          {/* STATUS */}
          <div className="space-y-4">

            <div className="bg-slate-900 rounded-3xl p-5 border border-cyan-500 shadow-2xl flex items-center gap-4">

              <FaEye className="text-cyan-400 text-4xl" />

              <div>
                <p className="text-gray-400">
                  Eye Status
                </p>

                <h2 className="text-2xl font-bold text-cyan-300">
                  Drowsy
                </h2>
              </div>

            </div>

            <div className="bg-slate-900 rounded-3xl p-5 border border-purple-500 shadow-2xl flex items-center gap-4">

              <FaPhone className="text-purple-400 text-4xl" />

              <div>
                <p className="text-gray-400">
                  Phone Usage
                </p>

                <h2 className="text-2xl font-bold text-purple-300">
                  Detected
                </h2>
              </div>

            </div>

            <div className="bg-slate-900 rounded-3xl p-5 border border-green-500 shadow-2xl flex items-center gap-4">

              <FaCarCrash className="text-green-400 text-4xl" />

              <div>
                <p className="text-gray-400">
                  Model Accuracy
                </p>

                <h2 className="text-2xl font-bold text-green-300">
                  99.94%
                </h2>
              </div>

            </div>

          </div>

        </div>

      </div>

    </div>
  );
}

export default App;

