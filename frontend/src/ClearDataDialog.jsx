import React, { useState } from 'react';
import { Trash2 } from 'lucide-react';

const ClearDataButton = () => {
  const [isClearing, setIsClearing] = useState(false);
  const [status, setStatus] = useState('');

  const handleClearData = async () => {
    setIsClearing(true);
    setStatus('');

    try {
      const apiEndpoint = import.meta.env.VITE_CLEAR_DATA_API_ENDPOINT;
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to clear data');
      }

      setStatus('Data cleared successfully');
      setTimeout(() => setStatus(''), 3000); // Clear status message after 3 seconds
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    } finally {
      setIsClearing(false);
    }
  };

  return (
    <div className="flex flex-col items-center">
      <button
        onClick={handleClearData}
        disabled={isClearing}
        className={`px-4 py-2 text-white bg-red-600 hover:bg-red-700 rounded flex items-center ${
          isClearing ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      >
        <Trash2 className="w-5 h-5 mr-2" />
        {isClearing ? 'Clearing...' : 'Clear Data'}
      </button>
      {status && (
        <div
          className={`mt-4 p-3 rounded ${
            status.includes('Error') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
          }`}
        >
          {status}
        </div>
      )}
    </div>
  );
};

export default ClearDataButton;
