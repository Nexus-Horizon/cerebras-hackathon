'use client';

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import ResultCard from '../components/ResultCard';
import LeaderboardTable from '../components/LeaderboardTable';
import toast from 'react-hot-toast';
// @ts-expect-error: Might generate error
import domtoimage from 'dom-to-image';
import { QRCodeSVG } from 'qrcode.react';

interface AnalysisResult {
  id: string;
  question: string;
  task: string;
  filename: string;
  result: string;
  latency: number;
  frontendTime: number;
  timestamp: number;
  modelName?: string;
  modelLatency?: number;
}

interface ModelLeaderboardEntry {
  model_name: string;
  latency: number;
  task: string;
}

export default function Home() {
  const [question, setQuestion] = useState('');
  const [image, setImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [frontendTime, setFrontendTime] = useState<number | null>(null);
  const [leaderboard, setLeaderboard] = useState<ModelLeaderboardEntry[]>([]);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const startTimeRef = useRef<number | null>(null);
  const qrRef = useRef<HTMLDivElement>(null)

  // Load leaderboard data on component mount
  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const response = await axios.get('http://localhost:8000/metrics/leaderboard', {
            params: { t: new Date().getTime() }
        });
        setLeaderboard(response.data);
      } catch (err) {
        console.error('Failed to fetch leaderboard:', err);
      }
    };

    fetchLeaderboard();
    // Refresh leaderboard every 30 seconds
    const interval = setInterval(fetchLeaderboard, 30000);
    return () => clearInterval(interval);
  }, []);

  // Apply dark mode class to document
  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  // Clean up preview URL when image changes
  useEffect(() => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    if (image) {
      const url = URL.createObjectURL(image);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }
  }, [image]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setImage(e.target.files[0]);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!image) {
      setError('Please select an image');
      return;
    }

    setIsSubmitting(true);
    setError(null);
    
    // Start frontend timer
    startTimeRef.current = Date.now();
    setFrontendTime(null);

    try {
      const formData = new FormData();
      formData.append('question', question);
      formData.append('image', image);

      const response = await axios.post('http://localhost:8000/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Stop frontend timer
      if (startTimeRef.current) {
        const endTime = Date.now();
        const frontendLatency = (endTime - startTimeRef.current) / 1000;
        setFrontendTime(frontendLatency);
      }

      const frontendLatency = startTimeRef.current ? (Date.now() - startTimeRef.current) / 1000 : 0;
      
      const newResult: AnalysisResult = {
        id: response.data.id,
        question,
        task: response.data.task,
        filename: response.data.filename,
        result: response.data.result,
        latency: response.data.latency,
        frontendTime: frontendLatency,
        timestamp: Date.now(),
        modelName: response.data.model
      };

      setResults(prev => [newResult, ...prev]);
      
      // Reset form after successful submission
      handleReset();
    } catch (err) {
      setError('Error occurred while submitting. Please try again.');
      console.error('Error:', err);
      
      // Stop frontend timer on error
      if (startTimeRef.current) {
        const endTime = Date.now();
        const frontendLatency = (endTime - startTimeRef.current) / 1000;
        setFrontendTime(frontendLatency);
      }
    } finally {
      setIsSubmitting(false);
      startTimeRef.current = null;
    }
  };

  const handleReset = () => {
    setQuestion('');
    setImage(null);
    setPreviewUrl(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDownload = (result: AnalysisResult) => {
    const content = `Task: ${result.task}\n\nFrontend Time: ${typeof result.frontendTime === 'number' && !isNaN(result.frontendTime) ? result.frontendTime.toFixed(2) : 'N/A'}s\n\nBackend Latency: ${typeof result.latency === 'number' && !isNaN(result.latency) ? result.latency.toFixed(2) : 'N/A'}s\n\nQuestion: ${result.question}\n\nResult: ${result.result}`;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    // Create a proper timestamp for the filename
    const timestamp = new Date(result.timestamp).toISOString().replace(/[:.]/g, '-').slice(0, -5);
    a.download = `${result.task}-${timestamp}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const downloadFixedPanelQR = () => {
    if (qrRef.current) {
      domtoimage.toPng(qrRef.current)
        .then((dataUrl: string) => {
          const link = document.createElement('a');
          link.download = `qr-code-${results[0]?.id ?? ''}.png`;
          link.href = dataUrl;
          link.click();
        })
        .catch(() => toast.error('Failed to download QR code'));
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              AutoModel
            </h1>
            <p className="text-gray-600">You ask. You upload. We analyze. Instantly.</p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="p-2 rounded-full bg-gray-200 hover:bg-gray-300 transition-colors duration-200"
              aria-label="Toggle dark mode"
            >
              {isDarkMode ? (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Form Section */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="px-6 py-6">
            <select 
              defaultValue={"local"}
              className="px-3 py-1 border border-gray-300 rounded-lg text-md focus:outline-none focus:ring-2 focus:ring-blue-500 mb-8 cursor-pointer"
              onChange={()=>{}}
            >
              <option value="local" className='rounded-lg'>Local Models</option>
            </select>
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  
                  <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-2">
                    Ask a question about the image
                  </label>
                  <input
                    type="text"
                    id="question"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    placeholder="e.g., What objects are in this image?"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="image" className="block text-sm font-medium text-gray-700 mb-2">
                    Upload Image (JPG or PNG)
                  </label>
                  <input
                    type="file"
                    id="image"
                    ref={fileInputRef}
                    onChange={handleImageChange}
                    accept="image/jpeg,image/png"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                    required
                  />
                  {image && (
                    <p className="mt-2 text-sm text-gray-500">
                      Selected: {image.name}
                    </p>
                  )}
                </div>

                {previewUrl && (
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Image Preview
                    </label>
                    <div className="border rounded-lg p-2 bg-gray-50">
                      <img 
                        src={previewUrl} 
                        alt="Preview" 
                        className="max-w-full h-48 object-contain mx-auto rounded-md"
                      />
                    </div>
                  </div>
                )}

                {error && (
                  <div className="text-red-500 text-sm bg-red-50 border border-red-200 rounded-lg p-3">
                    {error}
                  </div>
                )}

                {frontendTime !== null && (
                  <div className="text-sm text-gray-600 bg-gray-50 border border-gray-200 rounded-lg p-3">
                    Frontend time: {frontendTime.toFixed(2)}s
                  </div>
                )}

                <div className="flex space-x-4">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 transition-all duration-200 font-medium"
                  >
                    {isSubmitting ? (
                      <div className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Analyzing...
                      </div>
                    ) : 'Analyze Image'}
                  </button>
                  
                  <button
                    type="button"
                    onClick={handleReset}
                    className="flex-1 bg-gray-200 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200 font-medium"
                  >
                    Reset
                  </button>
                </div>
              </form>
            </div>
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-xl shadow-lg overflow-hidden">
            <div className="px-6 py-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Analysis Results</h2>
              
              {results.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p>No results yet. Upload an image and ask a question to get started.</p>
                </div>
              ) : (
                <div className="text-center space-y-4 max-h-96 overflow-y-auto">
                  {results.map((result, index) => (
                    <ResultCard
                      key={result.timestamp}
                      question={result.question}
                      task={result.task}
                      result={result.result}
                      latency={result.latency}
                      frontendTime={result.frontendTime || 0}
                      modelName={result.modelName}
                      modelLatency={result.modelLatency}
                      resultId={result.id}
                      onDownload={() => handleDownload(result)}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Speed Leaderboard Panel */}
          <div className="fixed top-4 right-4 w- bg-white rounded-xl shadow-lg overflow-hidden z-10">
            <div className="text-sm font-bold text-gray-900 p-3">Speed Leaderboard</div>
            <div className="text-sm">
              <LeaderboardTable />
            </div>
          </div>

          {/* Shareable Link */}
          <div className="fixed bottom-4 right-4 w-64 bg-white rounded-xl shadow-lg overflow-hidden z-10">
            <div className="text-sm font-bold text-gray-900 p-3">Share Result</div>
            <div className="text-center p-3">
              {results.length > 0 ? (
                <>
                  <div className="text-sm text-gray-600 mb-2">Scan QR code to share</div>
                  <div 
                    ref={qrRef} 
                  className="bg-white p-4 rounded-lg shadow-lg" 
                    onClick={e => e.stopPropagation()}
                  >
                    <div className="flex items-center justify-center p-4">
                    <QRCodeSVG value={`http://localhost:3000/result/${results[0].id}`} 
                    size={128} />
                    </div>
                    
                  </div>
                  
                  <div className="text-center mt-2">
                    <button 
                      onClick={() => {
                        navigator.clipboard.writeText(`http://localhost:3000/result/${results[0].id}`);
                        toast.success('Copied!');
                      }}
                      className="text-sm bg-blue-500 text-white py-1 px-3 rounded hover:bg-blue-600 transition-colors duration-200 mr-2"
                    >
                      Copy Link
                    </button>
                    <button 
                      onClick={downloadFixedPanelQR}
                      className="text-sm bg-gray-200 text-gray-700 py-1 px-3 rounded hover:bg-gray-300 transition-colors duration-200"
                    >
                      Download QR
                    </button>
                  </div>
                </>
              ) : (
                <div className="text-sm text-gray-500">No results to share</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
