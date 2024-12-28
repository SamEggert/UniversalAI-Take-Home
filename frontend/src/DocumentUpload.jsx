import React, { useState } from 'react';
import { Upload, File, X } from 'lucide-react';

function DocumentUpload() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState({});
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles(prev => [...prev, ...files]);
    setUploadStatus({});
  };

  const removeFile = (index) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
    setUploadStatus(prev => {
      const newStatus = { ...prev };
      delete newStatus[index];
      return newStatus;
    });
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setUploadStatus({ error: 'Please select files first' });
      return;
    }

    setIsUploading(true);
    const uploadResults = {};

    try {
      const apiEndpoint = import.meta.env.VITE_UPLOAD_API_ENDPOINT;

      // Upload files in parallel
      const uploadPromises = selectedFiles.map(async (file, index) => {
        try {
          const formData = new FormData();
          formData.append('file', file);

          const response = await fetch(apiEndpoint, {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) {
            throw new Error('Upload failed');
          }

          const result = await response.text();
          uploadResults[index] = { success: true, message: result };
        } catch (error) {
          uploadResults[index] = {
            success: false,
            message: `Failed to upload ${file.name}: ${error.message}`
          };
        }
      });

      await Promise.all(uploadPromises);
      setUploadStatus(uploadResults);

      // Clear successfully uploaded files
      setSelectedFiles(prev =>
        prev.filter((_, index) => !uploadResults[index]?.success)
      );
    } catch (error) {
      console.error('Upload error:', error);
      setUploadStatus({ error: `Upload failed: ${error.message}` });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
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
              Click to upload or drag and drop multiple files
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
            multiple
          />
        </label>
      </div>

      {selectedFiles.length > 0 && (
        <div className="mt-4">
          <h3 className="font-semibold mb-2">Selected Files:</h3>
          <div className="space-y-2">
            {selectedFiles.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="flex items-center justify-between p-2 bg-gray-50 rounded"
              >
                <span className="truncate flex-1">{file.name}</span>
                <button
                  onClick={() => removeFile(index)}
                  className="ml-2 p-1 text-gray-500 hover:text-red-500"
                  disabled={isUploading}
                >
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>

          <button
            onClick={handleUpload}
            disabled={isUploading}
            className={`w-full mt-4 py-2 px-4 rounded ${
              isUploading
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            {isUploading ? 'Uploading...' : `Upload ${selectedFiles.length} Files`}
          </button>
        </div>
      )}

      {Object.entries(uploadStatus).map(([index, status]) => (
        <div
          key={index}
          className={`mt-4 p-3 rounded ${
            status.success ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}
        >
          {status.message}
        </div>
      ))}
    </div>
  );
}

export default DocumentUpload;