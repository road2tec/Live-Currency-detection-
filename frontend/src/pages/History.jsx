import React, { useState, useEffect } from 'react';
import { historyService } from '../services/api';
import toast from 'react-hot-toast';
import { HiClock, HiCurrencyRupee, HiTrash, HiFilter, HiChevronLeft, HiChevronRight } from 'react-icons/hi';

const History = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    loadHistory();
  }, [page, filter]);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const response = await historyService.getHistory(page, 15, filter || null);
      const data = response.data.data;
      setHistory(data.history);
      setTotalPages(data.pages);
      setTotal(data.total);
    } catch (err) {
      toast.error('Failed to load history');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this detection record?')) return;
    try {
      await historyService.deleteItem(id);
      toast.success('Record deleted');
      loadHistory();
    } catch (err) {
      toast.error('Failed to delete');
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Clear ALL detection history? This cannot be undone.')) return;
    try {
      await historyService.clearHistory();
      toast.success('History cleared');
      setHistory([]);
      setTotal(0);
    } catch (err) {
      toast.error('Failed to clear history');
    }
  };

  const getConfidenceColor = (conf) => {
    if (conf >= 0.95) return 'text-green-600 bg-green-50';
    if (conf >= 0.85) return 'text-blue-600 bg-blue-50';
    if (conf >= 0.70) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 flex items-center space-x-3">
            <HiClock className="w-8 h-8 text-gray-600" />
            <span>Detection History</span>
          </h1>
          <p className="text-gray-500 mt-1">{total} total detections</p>
        </div>

        <div className="flex items-center gap-3">
          {/* Filter */}
          <div className="flex items-center space-x-2 bg-white rounded-xl border border-gray-200 px-3 py-2">
            <HiFilter className="w-4 h-4 text-gray-400" />
            <select
              value={filter}
              onChange={(e) => { setFilter(e.target.value); setPage(1); }}
              className="bg-transparent text-sm text-gray-700 outline-none"
            >
              <option value="">All Types</option>
              <option value="upload">Upload</option>
              <option value="live">Live</option>
              <option value="multi">Multi</option>
            </select>
          </div>

          {total > 0 && (
            <button
              onClick={handleClearAll}
              className="flex items-center space-x-1 px-4 py-2 bg-red-50 hover:bg-red-100 text-red-600 rounded-xl text-sm font-medium transition-colors"
            >
              <HiTrash className="w-4 h-4" />
              <span>Clear All</span>
            </button>
          )}
        </div>
      </div>

      {/* History List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
        </div>
      ) : history.length > 0 ? (
        <>
          <div className="space-y-3">
            {history.map((item) => (
              <div
                key={item.id}
                className="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow p-4"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                      item.is_fake ? 'bg-red-100' : 'bg-blue-100'
                    }`}>
                      <HiCurrencyRupee className={`w-6 h-6 ${item.is_fake ? 'text-red-600' : 'text-blue-600'}`} />
                    </div>

                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xl font-bold text-gray-900">₹{item.prediction}</span>
                        {item.is_fake && (
                          <span className="text-xs px-2 py-0.5 bg-red-100 text-red-700 rounded-full font-medium">
                            ⚠️ Suspicious
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-3 mt-1">
                        <span className="text-xs text-gray-400">
                          {new Date(item.date).toLocaleString()}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                          item.detection_type === 'live'
                            ? 'bg-purple-100 text-purple-700'
                            : item.detection_type === 'multi'
                            ? 'bg-orange-100 text-orange-700'
                            : 'bg-blue-100 text-blue-700'
                        }`}>
                          {item.detection_type}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <div className={`px-3 py-1.5 rounded-lg text-sm font-bold ${getConfidenceColor(item.confidence)}`}>
                      {(item.confidence * 100).toFixed(1)}%
                    </div>

                    <button
                      onClick={() => handleDelete(item.id)}
                      className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
                    >
                      <HiTrash className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {item.ocr_text && (
                  <div className="mt-3 px-4 py-2 bg-gray-50 rounded-lg">
                    <p className="text-xs text-gray-500 font-medium">OCR Text</p>
                    <p className="text-sm text-gray-700 truncate">{item.ocr_text}</p>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center space-x-3 mt-8">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 rounded-lg bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <HiChevronLeft className="w-5 h-5" />
              </button>

              <span className="text-sm text-gray-600">
                Page <span className="font-bold">{page}</span> of <span className="font-bold">{totalPages}</span>
              </span>

              <button
                onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="p-2 rounded-lg bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <HiChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-20 bg-white rounded-2xl border border-gray-100">
          <HiClock className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-medium text-gray-500 mb-2">No detection history</h3>
          <p className="text-gray-400">Start detecting currency to see your history here</p>
        </div>
      )}
    </div>
  );
};

export default History;
