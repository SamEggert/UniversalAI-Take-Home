import React, { useState } from "react";
import { FileText, Download, ExternalLink } from 'lucide-react';

function DocumentLink({ fileName = "Unknown Document", blobUrl }) {
  const isPdf = fileName.toLowerCase().endsWith(".pdf");
  return (
    <a
      href={blobUrl}
      download={!isPdf && fileName}
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
}

function Autocomplete() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState({ text: "", sources: [] });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const apiEndpoint = import.meta.env.VITE_AUTOCOMPLETE_API_ENDPOINT;
      const res = await fetch(apiEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const result = await res.json();
      setResponse(result);
    } catch (err) {
      console.error(err);
      setResponse({ text: "Error fetching response.", sources: [] });
    } finally {
      setLoading(false);
    }
  };

  const renderResponse = () => {
    if (!response.text) return null;

    // Parse response.text for document links using the response.sources
    const parts = [];
    const regex = /\[Document: ([^\]]+)\]/g;
    let lastIndex = 0;
    let match;

    while ((match = regex.exec(response.text)) !== null) {
      if (match.index > lastIndex) {
        parts.push(response.text.substring(lastIndex, match.index));
      }

      const fileName = match[1];
      const source = response.sources.find((src) => src.fileName === fileName);

      if (source) {
        parts.push(
          <DocumentLink
            key={fileName}
            fileName={fileName}
            blobUrl={source.blobUrl}
          />
        );
      } else {
        parts.push(match[0]);
      }

      lastIndex = regex.lastIndex;
    }

    if (lastIndex < response.text.length) {
      parts.push(response.text.substring(lastIndex));
    }

    return <div className="mt-4 p-3 bg-gray-100 rounded">{parts}</div>;
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">Autocomplete</h2>
      <textarea
        className="w-full p-2 border rounded"
        rows="4"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Type your query here..."
      />
      <button
        onClick={handleSubmit}
        disabled={loading}
        className="w-full mt-4 py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        {loading ? "Loading..." : "Submit"}
      </button>
      {renderResponse()}
    </div>
  );
}

export default Autocomplete;
