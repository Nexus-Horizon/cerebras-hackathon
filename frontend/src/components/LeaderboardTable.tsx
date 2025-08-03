'use client';

import { useEffect, useState } from 'react';

interface LeaderboardEntry {
  model: string;
  average_latency: number;
  runs: number;
}

export default function LeaderboardTable() {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const response = await fetch(`http://localhost:8000/leaderboard?ts=${Date.now()}`);
        const data = await response.json();
        setLeaderboard(data);
      } catch (error) {
        console.error('Failed to fetch leaderboard:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchLeaderboard();
    const interval = setInterval(fetchLeaderboard, 30000);
    
    const handleRefresh = () => fetchLeaderboard();
    window.addEventListener('leaderboard-refresh', handleRefresh);
    
    return () => {
      clearInterval(interval);
      window.removeEventListener('leaderboard-refresh', handleRefresh);
    };
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Check if there's no data
  if (leaderboard.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500 bg-gray-100 rounded-lg shadow">
        No leaderboard data yet
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4 bg-white rounded-lg shadow overflow-hidden">
      <div className="overflow-x-auto w-full">
        <table className="w-full border border-gray-300 text-sm">
          <thead>
            <tr className="bg-gray-100">
              <th scope="col" className="px-4 py-2 text-left font-medium text-gray-900">
                Model
              </th>
              <th scope="col" className="px-4 py-2 text-left font-medium text-gray-900">
                Avg Latency
              </th>
              <th scope="col" className="px-4 py-2 text-left font-medium text-gray-900">
                Runs
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-300">
            {leaderboard.map((entry, index) => (
              <tr 
                key={entry.model} 
                className={`hover:bg-gray-50 ${index === 0 ? 'bg-yellow-50' : 'bg-white'} block sm:table-row`}
              >
                <td className="px-4 py-2 hidden sm:table-cell">
                  <div className="flex items-center">
                    {index === 0 && (
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-yellow-200 text-yellow-800 mr-2">
                        🏆
                      </span>
                    )}
                    <span className="text-gray-900">{entry.model}</span>
                  </div>
                </td>
                <td className="px-4 py-2 text-gray-900 hidden sm:table-cell">
                  {entry.average_latency.toFixed(2)}s
                </td>
                <td className="px-4 py-2 text-gray-900 hidden sm:table-cell">
                  {entry.runs}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
