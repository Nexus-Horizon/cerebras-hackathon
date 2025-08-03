'use client';

import { useState, useEffect, useRef } from 'react';
import toast from 'react-hot-toast';
import { QRCodeSVG } from 'qrcode.react';
// @ts-expect-error: Might generate error
import domtoimage from 'dom-to-image';

interface ResultCardProps {
  question: string;
  task: string;
  result: string;
  latency: number;
  frontendTime: number;
  modelName?: string;
  modelLatency?: number;
  imageUrl?: string;
  resultId?: string;
  onDownload?: () => void;
}

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

export default function ResultCard({ 
  question, 
  task, 
  result, 
  latency, 
  frontendTime, 
  modelName,
  modelLatency,
  imageUrl,
  resultId,
  onDownload 
}: ResultCardProps) {
  const [showQR, setShowQR] = useState(false);
  const [qrCode, setQrCode] = useState<string | null>(null);
  const qrRef = useRef<HTMLDivElement>(null);
  
  const shareableLink = `http://localhost:3000/result/${resultId}`;

  const copyLink = () => {
    navigator.clipboard.writeText(shareableLink)
      .then(() => toast.success('📋 Copied!'))
      .catch(() => toast.error('Failed to copy link'));
  };

  const copyResult = (text: string) => {
    navigator.clipboard.writeText(text)
      .then(() => toast.success('Result copied!'))
      .catch(() => toast.error('Failed to copy result'));
  };

  const generateQR = () => {
    setQrCode(shareableLink);
    setShowQR(true);
  };

  const downloadQR = () => {
    if (qrRef.current) {
      domtoimage.toPng(qrRef.current)
        .then((dataUrl: string) => {
          const link = document.createElement('a');
          link.download = 'qr-code.png';
          link.href = dataUrl;
          link.click();
        })
        .catch(() => toast.error('Failed to download QR code'));
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

  const downloadText = () => {
    const text = result;
    const filename = `result-${task}-${Date.now()}.txt`;
    const blob = new Blob([text], { type: 'text/plain' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    toast.success('📥 Download started');
  };
  const [showCheckmark, setShowCheckmark] = useState(false);
  const [showConfetti, setShowConfetti] = useState(false);

  useEffect(() => {
    // Trigger checkmark animation when component mounts
    setShowCheckmark(true);
    
    // Show confetti animation for fast results
    if (latency < 0.3) {
      setShowConfetti(true);
    }
  }, [latency]);

  const getTaskColor = (taskName: string) => {
    switch (taskName.toLowerCase()) {
      case 'ocr':
        return 'bg-blue-100 border-blue-200';
      case 'captioning':
        return 'bg-green-100 border-green-200';
      case 'vqa':
        return 'bg-purple-100 border-purple-200';
      default:
        return 'bg-gray-100 border-gray-200';
    }
  };

  const getTaskIcon = (taskName: string) => {
    switch (taskName.toLowerCase()) {
      case 'ocr':
        return '📖';
      case 'captioning':
        return '🖼️';
      case 'vqa':
        return '🤖';
      default:
        return '❓';
    }
  };

  const getSpeedBadge = (latencyValue: number) => {
    if (typeof latencyValue !== 'number' || isNaN(latencyValue)) {
      return <span className="inline-items px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
        ⏱ Unknown
      </span>;
    }
    if (latencyValue < 1.0) {
      return <span className="inline-items px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 animate-pulse">
        ⚡ {latencyValue.toFixed(2)}s ✅
      </span>;
    } else {
      return <span className="inline-items px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
        ⏱ {latencyValue.toFixed(2)}s
      </span>;
    }
  };

  const getModelBadge = (modelLatencyValue: number) => {
    if (typeof modelLatencyValue !== 'number' || isNaN(modelLatencyValue)) {
      return <span className="inline-items px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
        ⏱ N/A
      </span>;
    }
    if (modelLatencyValue < 1.0) {
      return <span className="inline-items px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
        {modelLatencyValue.toFixed(2)}s ✅
      </span>;
    } else {
      return <span className="inline-items px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
        {modelLatencyValue.toFixed(2)}s
      </span>;
    }
  };

  return (
    <div className={`border rounded-lg p-4 mb-4 transition-all duration-300 ease-in-out ${getTaskColor(task)} shadow-sm hover:shadow-md transform`}>
      <h2 className="text-lg font-semibold mb-3 flex items-center text-grey-600">
        <span className="mr-2 text">🧠</span> Model Result
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-3">
        <div className="flex items-center space-x-2 p-2 bg-white rounded-lg border">
          <span className="text-xl">🧠</span>
          <div>
            <p className="text-sm font-medium text-gray-600">Task Detected</p>
            <p className="text-gray-800">{task}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 p-2 bg-white rounded-lg border">
          <span className="text-xl">🤖</span>
          <div>
            <p className="text-sm font-medium text-gray-600">Model Used</p>
            <p className="text-gray-800">{modelName || 'N/A'}</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 p-2 bg-white rounded-lg border">
          <span className="text-xl">⚡</span>
          <div>
            <p className="text-sm font-medium text-gray-600">Latency</p>
            <p className="text-gray-800">{latency.toFixed(2)}s</p>
          </div>
        </div>
      </div>
      
      {imageUrl && (
        <div className="mb-3">
          <p className="text-sm font-medium text-gray-600 flex items-center">
            <span className="text-xl mr-2">🖼️</span> Image
          </p>
          <img 
            src={imageUrl} 
            alt="Generated result" 
            className="w-full max-h-64 object-contain rounded-lg border"
          />
        </div>
      )}

      <div className="w-full flex flex-col col-reverse h-fit justify-start gap-2">
        <button
            onClick={copyLink}
            className="text-sm bg-blue-500 hover:bg-blue-600 text-white py-1 px-3 rounded-md transition-colors duration-200"
          >
            📋 Copy Result Link
          </button>
          
          </div>
          <br/>
      
      <div className="text-center mb-3">
        <p className="text-sm font-medium text-gray-600">Question:</p>
        <p className="text-gray-800">{question}</p>
      </div>
      
      <div className="flex flex-col justify-between items-center">
        <div>
          <p className="text-sm text-gray-600">
            Backend latency: {typeof latency === 'number' && !isNaN(latency) ? latency.toFixed(2) : 'N/A'}s
          </p>
          <p className="text-sm text-gray-600">
            Frontend time: {typeof frontendTime === 'number' && !isNaN(frontendTime) ? frontendTime.toFixed(2) : 'N/A'}s
          </p>
        </div>
        <div className="text-center space-x-2"><div>
          {showCheckmark && (
            <div className="text-green-500 animate-bounce">
              ✓
            </div>
          )}
          {showConfetti && (
            <div className="text-green-500 animate-bounce">
              ✨ Fast Result!
            </div>
          )}</div>
      <div className="w-full flex">{onDownload && (
            <button
              onClick={onDownload || handleDownload}
              className="flex w-full min-w-fit h-fit text-sm bg-gray-200 hover:bg-gray-300 text-gray-700 py-1 px-3 rounded-md transition-colors duration-200"
            >
              Download Metrics
            </button>
          )}
          
          <button
            onClick={generateQR}
            className="flex w-full min-w-fit text-sm bg-green-500 hover:bg-green-600 text-white py-1 px-3 rounded-md transition-colors duration-200 ml-2"
          >
            📱 Show QR
          </button></div>
          {showQR && (
            <div 
              className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" 
              onClick={() => setShowQR(false)}
            >
              <div 
                ref={qrRef} 
                className="bg-white p-4 rounded-lg shadow-lg" 
                onClick={e => e.stopPropagation()}
              >
                <div className="flex items-center justify-center p-4">
                  <QRCodeSVG value={qrCode || ''} size={200} />
                </div>
                <div className="text-center mt-4">
                  <button
                    onClick={downloadQR}
                    className="text-sm bg-blue-500 hover:bg-blue-600 text-white py-1 px-3 rounded-md transition-colors duration-200"
                  >
                    Download QR
                  </button>
                  <button
                    onClick={() => setShowQR(false)}
                    className="text-sm bg-gray-500 hover:bg-gray-600 text-white py-1 px-3 rounded-md transition-colors duration-200 ml-2"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          )}
          
        </div>
      </div>
    </div>
  );
}
