import React, { useState } from "react";

function Autocomplete() {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
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
      const result = await res.text();
      setResponse(result);
    } catch (err) {
      console.error(err);
      setResponse("Error fetching response.");
    } finally {
      setLoading(false);
    }
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
      {response && (
        <div className="mt-4 p-3 bg-gray-100 rounded">{response}</div>
      )}
    </div>
  );
}

export default Autocomplete;
