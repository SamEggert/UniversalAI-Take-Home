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
    context_parts = []
    for _, metadata, _ in results:
        doc_name = metadata.get('file_name', 'Unknown Document')  # Fallback if missing
        content = metadata.get('content', 'No content available')  # Fallback if missing
        formatted_content = f"[Document: {doc_name}]\n{content}"
        context_parts.append(formatted_content)
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
        embeddings_model = OpenAIEmbeddings(api_key=api_key)

        # Generate embedding for the query
        query_embedding = embeddings_model.embed_query(query)

        # Search for relevant documents
        search_results = search_embeddings(query_embedding)

        if not search_results:
            # No documents found; proceed with query-only prompt
            logging.info("No relevant documents found. Proceeding with query-only prompt.")
            prompt = f"""You are a helpful assistant. Answer the following question as best as you can without additional context:

Question: {query}

If you cannot provide a confident answer, acknowledge the lack of information.
"""

            # Initialize LLM
            llm = ChatOpenAI(api_key=api_key, temperature=0.5)

            # Generate response
            ai_message = llm.invoke(prompt)
            response_text = ai_message.content if hasattr(ai_message, "content") else "Unable to generate response."

            return func.HttpResponse(
                json.dumps({
                    "text": response_text,
                    "sources": []  # No sources available
                }),
                status_code=200,
                headers={**cors_headers, 'Content-Type': 'application/json'}
            )

        # Documents found; format context
        context = format_context(search_results)

        # Create prompt with context
        prompt = f"""Context:
{context}

Question: {query}

You are a helpful assistant. Your responses should:
1. Be brief and answer exactly what was asked.
2. Include relevant quotes from the context when necessary.
3. If the context does not contain an answer, acknowledge the lack of information.
"""

        # Initialize LangChain OpenAI instance
        llm = ChatOpenAI(api_key=api_key, temperature=0.5)

        # Generate response with context
        ai_message = llm.invoke(prompt)
        response_text = ai_message.content if hasattr(ai_message, "content") else "Unable to generate response."

        return func.HttpResponse(
            json.dumps({
                "text": response_text,
                "sources": format_response(response_text, search_results).get("sources", [])
            }),
            status_code=200,
            headers={**cors_headers, 'Content-Type': 'application/json'}
        )

    except Exception as e:
        logging.error(f"Error in autocomplete: {e}")
        return func.HttpResponse(
            json.dumps({"error": f"An error occurred: {str(e)}"}),
            status_code=500,
            headers={**cors_headers, 'Content-Type': 'application/json'}
        )
