import React, { useState } from 'react';
import { Upload, File } from 'lucide-react';

function DocumentUpload() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setUploadStatus('');
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a file first');
      return;
    }

    setIsUploading(true);
    setUploadStatus('Uploading...');

    try {
      // Create FormData to send the file
      const formData = new FormData();
      formData.append('file', selectedFile);

      // Get the API endpoint from environment variables
      const apiEndpoint = import.meta.env.VITE_UPLOAD_API_ENDPOINT;

      // Send the file to Azure Function
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        body: formData,
        headers: {
          'x-file-name': selectedFile.name,
        }
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const result = await response.json();
      setUploadStatus(`Upload successful! Processed ${result.chunk_count} chunks.`);
      setSelectedFile(null);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus(`Upload failed: ${error.message}`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4 flex items-center">
        <File className="mr-2" /> Document Upload
      </h2>

      <div className="flex items-center justify-center w-full">
        <label
          htmlFor="fileUpload"
          className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
        >
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            <Upload className="w-10 h-10 text-gray-400 mb-3" />
            <p className="mb-2 text-sm text-gray-500">
              {selectedFile
                ? `Selected: ${selectedFile.name}`
                : 'Click to upload or drag and drop'}
            </p>
            <p className="text-xs text-gray-400">
              Any document type supported
            </p>
          </div>
          <input
            id="fileUpload"
            type="file"
            className="hidden"
            onChange={handleFileChange}
          />
        </label>
      </div>

      {selectedFile && (
        <button
          onClick={handleUpload}
          disabled={isUploading}
          className={`w-full mt-4 py-2 px-4 rounded ${
            isUploading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          }`}
        >
          {isUploading ? 'Uploading...' : 'Upload Document'}
        </button>
      )}

      {uploadStatus && (
        <div className={`mt-4 p-3 rounded ${
          uploadStatus.includes('failed')
            ? 'bg-red-100 text-red-700'
            : 'bg-green-100 text-green-700'
        }`}>
          {uploadStatus}
        </div>
      )}
    </div>
  );
}

export default DocumentUpload;