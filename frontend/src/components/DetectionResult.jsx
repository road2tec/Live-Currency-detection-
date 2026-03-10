import React from 'react';
import { HiCurrencyRupee, HiShieldCheck, HiExclamation, HiCheckCircle } from 'react-icons/hi';

const DENOMINATION_COLORS = {
  10: { bg: 'bg-amber-50', border: 'border-amber-300', text: 'text-amber-800', accent: '#d97706' },
  20: { bg: 'bg-green-50', border: 'border-green-300', text: 'text-green-800', accent: '#059669' },
  50: { bg: 'bg-blue-50', border: 'border-blue-300', text: 'text-blue-800', accent: '#2563eb' },
  100: { bg: 'bg-purple-50', border: 'border-purple-300', text: 'text-purple-800', accent: '#7c3aed' },
  200: { bg: 'bg-orange-50', border: 'border-orange-300', text: 'text-orange-800', accent: '#ea580c' },
  500: { bg: 'bg-gray-50', border: 'border-gray-300', text: 'text-gray-800', accent: '#4b5563' },
  2000: { bg: 'bg-pink-50', border: 'border-pink-300', text: 'text-pink-800', accent: '#db2777' },
};

const DetectionResult = ({ result, showDetails = true }) => {
  if (!result) return null;

  const denomination = result.denomination || 0;
  const confidence = result.confidence || 0;
  const ocrText = result.ocr_text || '';
  const isFake = result.is_fake || false;
  const status = result.status || 'unknown';
  const processingTime = result.processing_time || 0;
  const colors = DENOMINATION_COLORS[denomination] || DENOMINATION_COLORS[500];

  const confidencePercent = (confidence * 100).toFixed(1);
  const confidenceColor = confidence >= 0.95 ? 'text-green-600' : confidence >= 0.85 ? 'text-blue-600' : confidence >= 0.7 ? 'text-yellow-600' : 'text-red-600';
  const confidenceBarColor = confidence >= 0.95 ? 'bg-green-500' : confidence >= 0.85 ? 'bg-blue-500' : confidence >= 0.7 ? 'bg-yellow-500' : 'bg-red-500';

  return (
    <div className={`rounded-2xl border-2 ${isFake ? 'border-red-400 bg-red-50' : `${colors.border} ${colors.bg}`} p-6 shadow-lg`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`w-14 h-14 rounded-xl ${isFake ? 'bg-red-100' : 'bg-white'} flex items-center justify-center shadow-sm`}>
            <HiCurrencyRupee className={`w-8 h-8 ${isFake ? 'text-red-500' : colors.text}`} />
          </div>
          <div>
            <h3 className={`text-3xl font-bold ${isFake ? 'text-red-700' : colors.text}`}>
              ₹{denomination}
            </h3>
            <p className="text-sm text-gray-500">Indian Rupee</p>
          </div>
        </div>

        {/* Status Badge */}
        <div className={`flex items-center space-x-1 px-3 py-1.5 rounded-full text-sm font-medium ${isFake ? 'bg-red-200 text-red-800' :
          status === 'confirmed' ? 'bg-green-200 text-green-800' :
            status === 'probable' ? 'bg-blue-200 text-blue-800' :
              'bg-yellow-200 text-yellow-800'
          }`}>
          {isFake ? <HiExclamation className="w-4 h-4" /> :
            status === 'confirmed' ? <HiShieldCheck className="w-4 h-4" /> :
              <HiCheckCircle className="w-4 h-4" />}
          <span>{isFake ? 'Potential Fake' : status === 'confirmed' ? 'Verified' : status === 'cnn_confident' ? 'High Confidence' : status === 'probable' ? 'Probable' : 'Uncertain'}</span>
        </div>
      </div>

      {/* Confidence Bar */}
      <div className="mb-4">
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-gray-600">Confidence</span>
          <span className={`text-lg font-bold ${confidenceColor}`}>{confidencePercent}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full ${confidenceBarColor} transition-all duration-1000`}
            style={{ width: `${Math.min(confidencePercent, 100)}%` }}
          />
        </div>
      </div>

      {showDetails && (
        <>
          {/* Removed raw OCR text display */}

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-3">

            {result.ocr_confidence !== undefined && (
              <div className="bg-white rounded-lg p-3 border border-gray-100">
                <p className="text-xs text-gray-500">OCR Confidence</p>
                <p className="text-sm font-semibold text-gray-800">{(result.ocr_confidence * 100).toFixed(1)}%</p>
              </div>
            )}
            {processingTime > 0 && (
              <div className="bg-white rounded-lg p-3 border border-gray-100">
                <p className="text-xs text-gray-500">Processing Time</p>
                <p className="text-sm font-semibold text-gray-800">{processingTime.toFixed(2)}s</p>
              </div>
            )}

          </div>
        </>
      )}
    </div>
  );
};

export default DetectionResult;
