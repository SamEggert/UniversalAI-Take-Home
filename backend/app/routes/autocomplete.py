# routes/autocomplete.py
import logging
import azure.functions as func
from app.utils.cors import cors_headers
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from app.services.vector_service import search_embeddings
import os
import json
from typing import List, Dict, Any

def format_context(results: List[tuple]) -> str:
    """Format the search results into a context string including document names."""
    context_parts = []
    for _, metadata, _ in results:
        if isinstance(metadata, dict) and 'content' in metadata:
            # Get the document name from file_name, defaulting to 'Unknown Document' if not present
            doc_name = metadata.get('file_name', 'Unknown Document')
            # Format the content with document name as a header
            formatted_content = f"[Document: {doc_name}]\n{metadata['content']}"
            context_parts.append(formatted_content)

    # Join all context parts with double newlines for separation
    return "\n\n".join(context_parts)

def format_response(response_text: str, search_results: List[tuple]) -> Dict[str, Any]:
    """Format the response with sources and their blob URLs."""
    sources = []
    for _, metadata, _ in search_results:
        if isinstance(metadata, dict):
            sources.append({
                "fileName": metadata.get('file_name', 'Unknown Document'),
                "blobUrl": metadata.get('blob_url', '')
            })

    return {
        "text": response_text,
        "sources": sources
    }

def autocomplete(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing autocomplete request with RAG.")

    # Handle CORS preflight
    if req.method == 'OPTIONS':
        return func.HttpResponse(status_code=200, headers=cors_headers)

    try:
        # Parse request body
        body = req.get_json()
        query = body.get("query", "")

        if not query:
            return func.HttpResponse(
                json.dumps({"error": "Query parameter is missing."}),
                status_code=400,
                headers={**cors_headers, 'Content-Type': 'application/json'}
            )

        # Fetch API key from environment variables
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables.")

        # Initialize embedding model
        embeddings_model = OpenAIEmbeddings(
            api_key=api_key,
            model="text-embedding-3-small"
        )

        # Generate embedding for the query
        query_embedding = embeddings_model.embed_query(query)

        # Search for relevant documents
        search_results = search_embeddings(query_embedding)

        # Format context from search results
        context = format_context(search_results)

        # Create prompt with context
        prompt = f"""Context:
{context}

Question: {query}

You are a helpful assistant. Your responses should:
1. Be brief and answer exactly what was asked
2. Your response should include quotes from documents as necessary and must not be very long
3. Include relevant quotes from the documents when needed
4. Not add any information beyond what's provided above
5. Please use quotations. You are directly quoting from the context.
6. When referencing documents, use the format [Document: filename] before each quote
7. If the context does not include a direct answer to the question, acknowledge that the source doesn't have the answer.

Example Document:
```
[Document: sample.pdf]
The system uses cloud storage and RAG pipelines. User interface includes document upload and chat.
```

Example Query: "What storage does the system use?"

Expected Answer:
According to [Document: sample.pdf], the system uses "cloud storage"
"""

        # Initialize LangChain OpenAI instance
        llm = ChatOpenAI(api_key=api_key, temperature=0.5)

        # Generate response with context
        ai_message = llm.invoke(prompt)

        # Extract the content of the AIMessage
        if hasattr(ai_message, "content"):
            response_text = ai_message.content
        else:
            raise ValueError("Unexpected response format from LangChain.")

        # Format response with sources
        sources = []
        for _, metadata, _ in search_results:
            if isinstance(metadata, dict):
                sources.append({
                    "fileName": metadata.get('file_name', 'Unknown Document'),
                    "blobUrl": metadata.get('blob_url', '')
                })

        formatted_response = {
            "text": response_text,
            "sources": sources
        }

        return func.HttpResponse(
            json.dumps(formatted_response),
            status_code=200,
            headers={
                **cors_headers,
                'Content-Type': 'application/json'
            }
        )

    except Exception as e:
        logging.error(f"Error in autocomplete: {e}")
        return func.HttpResponse(
            json.dumps({
                "error": f"An error occurred during processing: {str(e)}"
            }),
            status_code=500,
            headers={
                **cors_headers,
                'Content-Type': 'application/json'
            }
        )