import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { detectionService } from '../services/api';
import DetectionResultCard from '../components/DetectionResult';
import toast from 'react-hot-toast';
import { HiUpload, HiPhotograph, HiX, HiRefresh } from 'react-icons/hi';

const UploadDetect = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      if (selectedFile.size > 10 * 1024 * 1024) {
        toast.error('File too large. Max size is 10MB.');
        return;
      }
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setResult(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'image/*': ['.jpg', '.jpeg', '.png', '.bmp', '.webp'] },
    maxFiles: 1,
    multiple: false,
  });

  const handleDetect = async () => {
    if (!file) {
      toast.error('Please select an image first');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await detectionService.detectImage(file);
      if (response.data.success) {
        setResult(response.data.data);
        toast.success(`Detected ₹${response.data.data.denomination}!`);
      } else {
        toast.error('Detection failed');
      }
    } catch (err) {
      const msg = err.response?.data?.detail || 'Detection failed. Please try again.';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null);
    setPreview(null);
    setResult(null);
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
          <HiUpload className="w-8 h-8 text-blue-600" />
          <span>Upload Detection</span>
        </h1>
        <p className="text-gray-500 mt-1">Upload a currency note image for AI-powered denomination detection</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Upload Area */}
        <div>
          {!preview ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all ${
                isDragActive
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 bg-gray-50 hover:border-blue-400 hover:bg-blue-50/50'
              }`}
            >
              <input {...getInputProps()} />
              <HiPhotograph className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <p className="text-lg font-medium text-gray-700 mb-2">
                {isDragActive ? 'Drop your image here' : 'Drag & drop currency image'}
              </p>
              <p className="text-sm text-gray-500 mb-4">or click to browse files</p>
              <p className="text-xs text-gray-400">Supports: JPG, PNG, BMP, WebP (Max 10MB)</p>
            </div>
          ) : (
            <div className="relative">
              <img
                src={preview}
                alt="Currency preview"
                className="w-full rounded-2xl shadow-lg border border-gray-200 object-contain max-h-[400px]"
              />
              <button
                onClick={handleReset}
                className="absolute top-3 right-3 p-2 bg-red-500 hover:bg-red-600 text-white rounded-full shadow-lg transition-colors"
              >
                <HiX className="w-5 h-5" />
              </button>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 mt-4">
            <button
              onClick={handleDetect}
              disabled={!file || loading}
              className="flex-1 flex items-center justify-center space-x-2 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold shadow-md disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white" />
                  <span>Detecting...</span>
                </>
              ) : (
                <>
                  <HiUpload className="w-5 h-5" />
                  <span>Detect Currency</span>
                </>
              )}
            </button>

            {result && (
              <button
                onClick={handleReset}
                className="flex items-center space-x-2 px-4 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-medium transition-all"
              >
                <HiRefresh className="w-5 h-5" />
                <span>New</span>
              </button>
            )}
          </div>
        </div>

        {/* Result Area */}
        <div>
          {loading && (
            <div className="flex flex-col items-center justify-center p-12 bg-white rounded-2xl border border-gray-100 shadow-sm">
              <div className="relative w-20 h-20 mb-4">
                <div className="absolute inset-0 rounded-full border-4 border-blue-200" />
                <div className="absolute inset-0 rounded-full border-4 border-blue-600 border-t-transparent animate-spin" />
              </div>
              <p className="text-lg font-medium text-gray-700">Analyzing currency...</p>
              <p className="text-sm text-gray-400 mt-1">Running AI detection pipeline</p>
            </div>
          )}

          {result && !loading && (
            <DetectionResultCard result={result} showDetails={true} />
          )}

          {!result && !loading && (
            <div className="flex flex-col items-center justify-center p-12 bg-gray-50 rounded-2xl border border-gray-100 text-center">
              <HiPhotograph className="w-16 h-16 text-gray-300 mb-4" />
              <p className="text-gray-500 font-medium">No detection yet</p>
              <p className="text-sm text-gray-400 mt-1">Upload an image to start</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UploadDetect;
