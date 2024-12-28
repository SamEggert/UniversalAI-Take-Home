import React, { useState } from 'react';
import { Trash2 } from 'lucide-react';

const ClearDataDialog = () => {
  const [isOpen, setIsOpen] = useState(false);
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
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to clear data');
      }

      setStatus('Data cleared successfully');
      setTimeout(() => {
        setIsOpen(false);
        setStatus('');
      }, 2000);
    } catch (error) {
      setStatus(`Error: ${error.message}`);
    } finally {
      setIsClearing(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className="mx-4 text-lg text-red-600 hover:text-red-800 flex items-center"
      >
        <Trash2 className="w-5 h-5 mr-2" />
        Clear Data
      </button>

      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Clear All Data</h2>
            <p className="mb-6 text-gray-600">
              Are you sure you want to clear all uploaded documents and their associated data? This action cannot be undone.
            </p>

            {status && (
              <div className={`mb-4 p-3 rounded ${
                status.includes('Error')
                  ? 'bg-red-100 text-red-700'
                  : 'bg-green-100 text-green-700'
              }`}>
                {status}
              </div>
            )}

            <div className="flex justify-end gap-4">
              <button
                onClick={() => setIsOpen(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800 bg-gray-100 hover:bg-gray-200 rounded"
                disabled={isClearing}
              >
                Cancel
              </button>
              <button
                onClick={handleClearData}
                disabled={isClearing}
                className="px-4 py-2 text-white bg-red-600 hover:bg-red-700 rounded flex items-center"
              >
                {isClearing ? (
                  <>
                    <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Clearing...
                  </>
                ) : (
                  'Clear All Data'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ClearDataDialog;