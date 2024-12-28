import React from "react";
import { FileText, Download, ExternalLink } from 'lucide-react';

const DocumentLink = ({ fileName, blobUrl }) => {
  const isPdf = fileName.toLowerCase().endsWith('.pdf');

  return (
    <a
      href={blobUrl}
      download={!isPdf && fileName}  // Only add download attribute for non-PDFs
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center text-blue-600 hover:text-blue-800 mx-1"
    >
      <FileText className="w-4 h-4 mr-1" />
      {fileName}
      {isPdf ? (
        <ExternalLink className="w-3 h-3 ml-1" />
      ) : (
        <Download className="w-3 h-3 ml-1" />
      )}
    </a>
  );
};

export default DocumentLink;