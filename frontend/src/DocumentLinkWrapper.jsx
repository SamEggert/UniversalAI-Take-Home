import React from 'react';
import { FileText, Download, ExternalLink } from 'lucide-react';

const DocumentLink = ({ fileName, blobUrl }) => {
  const isPdf = fileName.toLowerCase().endsWith('.pdf');

  const handleClick = (e) => {
    e.preventDefault();
    if (isPdf) {
      // Open PDF in new tab
      window.open(blobUrl, '_blank');
    } else {
      // For other files, trigger download
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
    <a
      href={blobUrl}
      onClick={handleClick}
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

// This component will wrap the chat response and parse document references
const DocumentLinkWrapper = ({ response }) => {
  // Regular expression to match document references in the format [Document: filename]
  const DOC_PATTERN = /\[Document: ([^\]]+)\]/g;

  // Split the response into parts and replace document references with links
  const parts = [];
  let lastIndex = 0;
  let match;

  // Reset the regex
  DOC_PATTERN.lastIndex = 0;

  while ((match = DOC_PATTERN.exec(response.text)) !== null) {
    // Add text before the match
    if (match.index > lastIndex) {
      parts.push(response.text.substring(lastIndex, match.index));
    }

    // Find the document URL from the sources
    const fileName = match[1];
    const source = response.sources.find(s => s.fileName === fileName);

    if (source) {
      // Add the document link component
      parts.push(
        <DocumentLink
          key={`doc-${match.index}`}
          fileName={fileName}
          blobUrl={source.blobUrl}
        />
      );
    } else {
      // If no matching source found, just add the text
      parts.push(match[0]);
    }

    lastIndex = DOC_PATTERN.lastIndex;
  }

  // Add any remaining text
  if (lastIndex < response.text.length) {
    parts.push(response.text.substring(lastIndex));
  }

  return <div className="chat-response">{parts}</div>;
};

export default DocumentLinkWrapper;