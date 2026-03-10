import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import DetectionResultCard from '../components/DetectionResult';
import { HiArrowLeft, HiCurrencyRupee } from 'react-icons/hi';

const Results = () => {
  const location = useLocation();
  const result = location.state?.result;

  if (!result) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <HiCurrencyRupee className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-gray-700 mb-2">No Results</h2>
        <p className="text-gray-500 mb-6">No detection results to display. Try detecting a currency note first.</p>
        <Link
          to="/detect"
          className="inline-flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 transition-colors"
        >
          <HiArrowLeft className="w-5 h-5" />
          <span>Go to Upload Detection</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <Link
          to="/detect"
          className="inline-flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors mb-4"
        >
          <HiArrowLeft className="w-5 h-5" />
          <span>Back to Detection</span>
        </Link>
        <h1 className="text-3xl font-bold text-gray-900">Detection Results</h1>
      </div>

      <DetectionResultCard result={result} showDetails={true} />

      {/* Action buttons */}
      <div className="flex gap-3 mt-6">
        <Link
          to="/detect"
          className="flex-1 text-center py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold transition-colors"
        >
          Detect Another
        </Link>
        <Link
          to="/history"
          className="flex-1 text-center py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl font-semibold transition-colors"
        >
          View History
        </Link>
      </div>
    </div>
  );
};

export default Results;
