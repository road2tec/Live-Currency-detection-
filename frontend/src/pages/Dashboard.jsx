import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { historyService } from '../services/api';
import { HiUpload, HiCamera, HiClock, HiCurrencyRupee, HiTrendingUp, HiShieldCheck, HiExclamation, HiChartBar } from 'react-icons/hi';
import { Doughnut, Bar } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentHistory, setRecentHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [statsRes, historyRes] = await Promise.all([
        historyService.getStats(),
        historyService.getHistory(1, 5),
      ]);
      setStats(statsRes.data.data);
      setRecentHistory(historyRes.data.data.history);
    } catch (err) {
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  const denomColors = {
    '10': '#d97706', '20': '#059669', '50': '#2563eb',
    '100': '#7c3aed', '200': '#ea580c', '500': '#4b5563', '2000': '#db2777',
  };

  const doughnutData = stats?.denomination_distribution ? {
    labels: Object.keys(stats.denomination_distribution).map(d => `₹${d}`),
    datasets: [{
      data: Object.values(stats.denomination_distribution),
      backgroundColor: Object.keys(stats.denomination_distribution).map(d => denomColors[d] || '#6b7280'),
      borderWidth: 2,
      borderColor: '#fff',
    }],
  } : null;

  const barData = stats?.denomination_distribution ? {
    labels: Object.keys(stats.denomination_distribution).map(d => `₹${d}`),
    datasets: [{
      label: 'Detections',
      data: Object.values(stats.denomination_distribution),
      backgroundColor: Object.keys(stats.denomination_distribution).map(d => `${denomColors[d] || '#6b7280'}80`),
      borderColor: Object.keys(stats.denomination_distribution).map(d => denomColors[d] || '#6b7280'),
      borderWidth: 2,
      borderRadius: 8,
    }],
  } : null;

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4" />
          <p className="text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Welcome */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, <span className="text-blue-600">{user?.name || 'User'}</span>! 👋
        </h1>
        <p className="text-gray-500 mt-1">Here's your currency detection overview</p>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Link to="/detect" className="group flex items-center space-x-4 p-6 bg-gradient-to-br from-blue-500 to-blue-700 rounded-2xl text-white shadow-lg shadow-blue-500/25 hover:shadow-xl hover:shadow-blue-500/40 transition-all">
          <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center group-hover:scale-110 transition-transform">
            <HiUpload className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-lg">Upload Detection</h3>
            <p className="text-blue-200 text-sm">Upload currency image</p>
          </div>
        </Link>

        <Link to="/live-detect" className="group flex items-center space-x-4 p-6 bg-gradient-to-br from-purple-500 to-purple-700 rounded-2xl text-white shadow-lg shadow-purple-500/25 hover:shadow-xl hover:shadow-purple-500/40 transition-all">
          <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center group-hover:scale-110 transition-transform">
            <HiCamera className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-lg">Live Camera</h3>
            <p className="text-purple-200 text-sm">Real-time detection</p>
          </div>
        </Link>

        <Link to="/history" className="group flex items-center space-x-4 p-6 bg-gradient-to-br from-gray-700 to-gray-900 rounded-2xl text-white shadow-lg shadow-gray-500/25 hover:shadow-xl hover:shadow-gray-500/40 transition-all">
          <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center group-hover:scale-110 transition-transform">
            <HiClock className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-bold text-lg">Detection History</h3>
            <p className="text-gray-300 text-sm">View past results</p>
          </div>
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <HiChartBar className="w-8 h-8 text-blue-500" />
            <span className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded-full">Total</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats?.total_detections || 0}</p>
          <p className="text-sm text-gray-500">Total Detections</p>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <HiTrendingUp className="w-8 h-8 text-green-500" />
            <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-1 rounded-full">Avg</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{((stats?.average_confidence || 0) * 100).toFixed(1)}%</p>
          <p className="text-sm text-gray-500">Avg Confidence</p>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <HiUpload className="w-8 h-8 text-purple-500" />
            <span className="text-xs font-medium text-purple-600 bg-purple-50 px-2 py-1 rounded-full">Upload</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats?.upload_detections || 0}</p>
          <p className="text-sm text-gray-500">Image Uploads</p>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <HiExclamation className="w-8 h-8 text-red-500" />
            <span className="text-xs font-medium text-red-600 bg-red-50 px-2 py-1 rounded-full">Alert</span>
          </div>
          <p className="text-3xl font-bold text-gray-900">{stats?.fake_detections || 0}</p>
          <p className="text-sm text-gray-500">Fake Alerts</p>
        </div>
      </div>

      {/* Charts & Recent History */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Charts */}
        <div className="space-y-6">
          {doughnutData && (
            <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
              <h3 className="font-bold text-gray-900 mb-4">Denomination Distribution</h3>
              <div className="max-w-[280px] mx-auto">
                <Doughnut data={doughnutData} options={{ responsive: true, plugins: { legend: { position: 'bottom' } } }} />
              </div>
            </div>
          )}
          {barData && (
            <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
              <h3 className="font-bold text-gray-900 mb-4">Detection Count</h3>
              <Bar data={barData} options={{ responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }} />
            </div>
          )}
        </div>

        {/* Recent History */}
        <div className="bg-white rounded-2xl p-6 border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-gray-900">Recent Detections</h3>
            <Link to="/history" className="text-sm text-blue-600 hover:text-blue-700 font-medium">View all →</Link>
          </div>
          {recentHistory.length > 0 ? (
            <div className="space-y-3">
              {recentHistory.map((item) => (
                <div key={item.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                      <HiCurrencyRupee className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">₹{item.prediction}</p>
                      <p className="text-xs text-gray-500">{new Date(item.date).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className={`text-sm font-bold ${item.confidence >= 0.9 ? 'text-green-600' : item.confidence >= 0.7 ? 'text-blue-600' : 'text-yellow-600'}`}>
                      {(item.confidence * 100).toFixed(1)}%
                    </p>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      item.detection_type === 'live' ? 'bg-purple-100 text-purple-700' : 'bg-blue-100 text-blue-700'
                    }`}>
                      {item.detection_type}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-400">
              <HiClock className="w-12 h-12 mx-auto mb-2" />
              <p>No detections yet</p>
              <Link to="/detect" className="text-blue-600 text-sm font-medium mt-2 inline-block">Start detecting →</Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
