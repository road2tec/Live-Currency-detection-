import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { HiCurrencyRupee, HiCamera, HiUpload, HiShieldCheck, HiLightningBolt, HiEye, HiChip } from 'react-icons/hi';

const Home = () => {
  const { isAuthenticated } = useAuth();

  const features = [
    {
      icon: <HiUpload className="w-8 h-8" />,
      title: 'Upload Detection',
      description: 'Upload currency images for instant AI-powered denomination detection with 97-99% accuracy.',
      color: 'from-blue-500 to-blue-600',
    },
    {
      icon: <HiCamera className="w-8 h-8" />,
      title: 'Live Camera Detection',
      description: 'Real-time currency detection using your webcam with 95-98% accuracy.',
      color: 'from-purple-500 to-purple-600',
    },
    {
      icon: <HiShieldCheck className="w-8 h-8" />,
      title: 'Fake Note Detection',
      description: 'Advanced OCR verification to identify potential counterfeit notes.',
      color: 'from-red-500 to-red-600',
    },
    {
      icon: <HiEye className="w-8 h-8" />,
      title: 'OCR Verification',
      description: 'Google Vision API validates text on currency notes for extra verification.',
      color: 'from-green-500 to-green-600',
    },
    {
      icon: <HiChip className="w-8 h-8" />,
      title: 'Multi-Stage AI Pipeline',
      description: 'YOLOv8 detection → ResNet50 CNN classification → OCR validation.',
      color: 'from-orange-500 to-orange-600',
    },
    {
      icon: <HiLightningBolt className="w-8 h-8" />,
      title: 'Multi-Note Detection',
      description: 'Detect and classify multiple currency notes in a single image.',
      color: 'from-yellow-500 to-yellow-600',
    },
  ];

  const denominations = [10, 20, 50, 100, 200, 500, 2000];

  return (
    <div className="overflow-hidden">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white min-h-[85vh] flex items-center">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-20 left-10 w-72 h-72 bg-orange-500 rounded-full blur-3xl" />
          <div className="absolute bottom-20 right-10 w-96 h-96 bg-green-500 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-blue-500 rounded-full blur-3xl" />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 relative z-10">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full mb-8">
              <HiChip className="w-5 h-5 text-blue-400" />
              <span className="text-sm font-medium text-blue-200">YOLOv8 + ResNet50 + OCR Pipeline</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight">
              <span className="text-orange-400">Indian</span>{' '}
              <span className="text-white">Currency</span>{' '}
              <span className="text-green-400">Detection</span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-300 mb-10 max-w-3xl mx-auto leading-relaxed">
              AI-powered system that detects and classifies Indian currency notes with
              <span className="text-blue-400 font-bold"> up to 99% accuracy</span> using deep learning,
              computer vision, and OCR verification.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
              {isAuthenticated ? (
                <>
                  <Link to="/detect" className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold text-lg shadow-xl shadow-blue-600/30 hover:shadow-blue-600/50 transition-all flex items-center space-x-2">
                    <HiUpload className="w-5 h-5" />
                    <span>Upload & Detect</span>
                  </Link>
                  <Link to="/live-detect" className="px-8 py-4 bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white rounded-xl font-semibold text-lg border border-white/20 transition-all flex items-center space-x-2">
                    <HiCamera className="w-5 h-5" />
                    <span>Live Camera</span>
                  </Link>
                </>
              ) : (
                <>
                  <Link to="/register" className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-semibold text-lg shadow-xl shadow-blue-600/30 hover:shadow-blue-600/50 transition-all">
                    Get Started Free
                  </Link>
                  <Link to="/login" className="px-8 py-4 bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white rounded-xl font-semibold text-lg border border-white/20 transition-all">
                    Sign In
                  </Link>
                </>
              )}
            </div>

            {/* Denomination chips */}
            <div className="flex flex-wrap items-center justify-center gap-3">
              <span className="text-sm text-gray-400">Supports:</span>
              {denominations.map((d) => (
                <span key={d} className="px-4 py-1.5 bg-white/10 backdrop-blur-sm rounded-full text-sm font-medium text-white border border-white/10">
                  ₹{d}
                </span>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Powerful AI Features</h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Built with state-of-the-art deep learning models for maximum accuracy and reliability.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, idx) => (
              <div key={idx} className="group p-8 bg-white rounded-2xl border border-gray-100 hover:border-gray-200 shadow-sm hover:shadow-xl transition-all duration-300">
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-r ${feature.color} flex items-center justify-center text-white mb-5 group-hover:scale-110 transition-transform`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pipeline Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Detection Pipeline</h2>
            <p className="text-lg text-gray-600">Multi-stage AI pipeline for maximum accuracy</p>
          </div>

          <div className="flex flex-col md:flex-row items-center justify-center gap-6">
            {[
              { step: '1', title: 'YOLO Detection', desc: 'Locate currency region', icon: '🔍' },
              { step: '2', title: 'CNN Classification', desc: 'Classify denomination', icon: '🧠' },
              { step: '3', title: 'OCR Verification', desc: 'Validate text on note', icon: '📝' },
              { step: '4', title: 'Final Decision', desc: 'Confidence voting', icon: '✅' },
            ].map((step, idx) => (
              <React.Fragment key={step.step}>
                <div className="bg-white rounded-2xl p-6 shadow-md border border-gray-100 text-center min-w-[200px]">
                  <div className="text-4xl mb-3">{step.icon}</div>
                  <div className="text-xs font-bold text-blue-600 mb-1">STAGE {step.step}</div>
                  <h4 className="font-bold text-gray-900 mb-1">{step.title}</h4>
                  <p className="text-sm text-gray-500">{step.desc}</p>
                </div>
                {idx < 3 && (
                  <div className="hidden md:block text-3xl text-gray-300">→</div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <HiCurrencyRupee className="w-6 h-6 text-blue-400" />
            <span className="text-xl font-bold text-white">CurrencyAI</span>
          </div>
          <p className="text-sm mb-4">Indian Currency Detection System powered by YOLOv8 + ResNet50 + OCR</p>
          <p className="text-xs text-gray-500">© 2026 CurrencyAI. Built with FastAPI, React, PyTorch.</p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
