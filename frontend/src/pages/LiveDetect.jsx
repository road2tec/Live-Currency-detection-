import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import { detectionService } from '../services/api';
import DetectionResultCard from '../components/DetectionResult';
import toast from 'react-hot-toast';
import { HiCamera, HiPlay, HiStop, HiSwitchHorizontal, HiCurrencyRupee } from 'react-icons/hi';

const LiveDetect = () => {
  const webcamRef = useRef(null);
  const intervalRef = useRef(null);
  const [isDetecting, setIsDetecting] = useState(false);
  const [result, setResult] = useState(null);
  const [facingMode, setFacingMode] = useState('environment');
  const [cameraReady, setCameraReady] = useState(false);
  const [captureCount, setCaptureCount] = useState(0);

  const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: facingMode,
  };

  // Capture and detect a single frame
  const captureAndDetect = useCallback(async () => {
    if (!webcamRef.current) return;

    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    try {
      const response = await detectionService.liveDetect(imageSrc);
      if (response.data.success && response.data.data.denomination > 0) {
        setResult(response.data.data);
        setCaptureCount((c) => c + 1);
      }
    } catch (err) {
      // Silent fail for live detection — log only
      console.error('Live detection error:', err.message);
    }
  }, []);

  // Start continuous detection
  const startDetection = useCallback(() => {
    setIsDetecting(true);
    setCaptureCount(0);
    toast.success('Live detection started! 📷');

    // Capture every 2 seconds
    intervalRef.current = setInterval(() => {
      captureAndDetect();
    }, 2000);
  }, [captureAndDetect]);

  // Stop continuous detection
  const stopDetection = useCallback(() => {
    setIsDetecting(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    toast('Detection stopped', { icon: '⏹️' });
  }, []);

  // Single capture
  const singleCapture = useCallback(async () => {
    toast.loading('Detecting...', { id: 'single-detect' });
    await captureAndDetect();
    toast.dismiss('single-detect');
    toast.success('Capture analyzed!');
  }, [captureAndDetect]);

  // Toggle camera
  const toggleCamera = () => {
    setFacingMode((prev) => (prev === 'user' ? 'environment' : 'user'));
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
          <HiCamera className="w-8 h-8 text-purple-600" />
          <span>Live Camera Detection</span>
        </h1>
        <p className="text-gray-500 mt-1">Point your camera at Indian currency notes for real-time detection</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Camera View */}
        <div>
          <div className="relative rounded-2xl overflow-hidden bg-black shadow-xl">
            <Webcam
              ref={webcamRef}
              audio={false}
              screenshotFormat="image/jpeg"
              screenshotQuality={0.8}
              videoConstraints={videoConstraints}
              onUserMedia={() => setCameraReady(true)}
              onUserMediaError={() => {
                toast.error('Camera access denied');
                setCameraReady(false);
              }}
              className="w-full"
            />

            {/* Overlay */}
            {isDetecting && (
              <div className="absolute inset-0 pointer-events-none">
                {/* Scanning border animation */}
                <div className="absolute inset-4 border-2 border-blue-400 rounded-xl detection-pulse" />
                {/* Status badge */}
                <div className="absolute top-3 left-3 flex items-center space-x-2 bg-red-500 text-white px-3 py-1.5 rounded-full text-sm font-medium shadow-lg">
                  <div className="w-2 h-2 bg-white rounded-full animate-pulse" />
                  <span>DETECTING</span>
                </div>
                {/* Capture counter */}
                <div className="absolute top-3 right-3 bg-black/60 text-white px-3 py-1.5 rounded-full text-sm font-medium">
                  Frames: {captureCount}
                </div>
              </div>
            )}

            {/* Denomination overlay when detected */}
            {result && result.denomination > 0 && (
              <div className="absolute bottom-3 left-3 right-3 bg-black/70 backdrop-blur-sm rounded-xl p-3 flex items-center justify-between text-white">
                <div className="flex items-center space-x-2">
                  <HiCurrencyRupee className="w-6 h-6 text-yellow-400" />
                  <span className="text-2xl font-bold">₹{result.denomination}</span>
                </div>
                <span className={`text-sm font-medium px-2 py-1 rounded-full ${
                  result.confidence >= 0.9 ? 'bg-green-500/30 text-green-300' : 'bg-yellow-500/30 text-yellow-300'
                }`}>
                  {(result.confidence * 100).toFixed(1)}%
                </span>
              </div>
            )}
          </div>

          {/* Controls */}
          <div className="flex gap-3 mt-4">
            {!isDetecting ? (
              <button
                onClick={startDetection}
                disabled={!cameraReady}
                className="flex-1 flex items-center justify-center space-x-2 py-3 bg-green-600 hover:bg-green-700 text-white rounded-xl font-semibold shadow-md disabled:opacity-50 transition-all"
              >
                <HiPlay className="w-5 h-5" />
                <span>Start Live Detection</span>
              </button>
            ) : (
              <button
                onClick={stopDetection}
                className="flex-1 flex items-center justify-center space-x-2 py-3 bg-red-600 hover:bg-red-700 text-white rounded-xl font-semibold shadow-md transition-all"
              >
                <HiStop className="w-5 h-5" />
                <span>Stop Detection</span>
              </button>
            )}

            <button
              onClick={singleCapture}
              disabled={!cameraReady || isDetecting}
              className="flex items-center space-x-2 px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium shadow-md disabled:opacity-50 transition-all"
            >
              <HiCamera className="w-5 h-5" />
              <span>Capture</span>
            </button>

            <button
              onClick={toggleCamera}
              className="p-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl transition-all"
              title="Switch camera"
            >
              <HiSwitchHorizontal className="w-5 h-5" />
            </button>
          </div>

          {!cameraReady && (
            <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-xl text-sm text-yellow-700">
              ⚠️ Camera not ready. Please allow camera access when prompted.
            </div>
          )}
        </div>

        {/* Result Area */}
        <div>
          {result ? (
            <DetectionResultCard result={result} showDetails={true} />
          ) : (
            <div className="flex flex-col items-center justify-center p-12 bg-gray-50 rounded-2xl border border-gray-100 text-center min-h-[300px]">
              <HiCamera className="w-16 h-16 text-gray-300 mb-4" />
              <p className="text-gray-500 font-medium">No detection yet</p>
              <p className="text-sm text-gray-400 mt-1">Start live detection or capture a frame</p>
            </div>
          )}

          {/* Instructions */}
          <div className="mt-6 bg-blue-50 rounded-xl p-5 border border-blue-100">
            <h4 className="font-bold text-blue-900 mb-2">📋 Instructions</h4>
            <ul className="text-sm text-blue-700 space-y-1.5">
              <li>• Hold the currency note flat in front of the camera</li>
              <li>• Ensure good lighting conditions</li>
              <li>• Keep the note centered in the camera frame</li>
              <li>• Live mode captures every 2 seconds automatically</li>
              <li>• Use "Capture" for single frame detection</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveDetect;
