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
    """Format the search results into a context string using full content."""
    context_parts = []
    for _, metadata, _ in results:
        # Extract the full content from metadata
        if isinstance(metadata, dict) and 'content' in metadata:
            context_parts.append(metadata['content'])

    return "\n\n".join(context_parts)

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
                "Query parameter is missing.",
                status_code=400,
                headers=cors_headers
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
        search_results = search_embeddings(query_embedding, top_k=3)

        # Format context from search results
        context = format_context(search_results)

        # Create prompt with context
        prompt = f"""Answer the following question using the provided context. If the context doesn't contain relevant information, say so.

Context:
{context}

Question: {query}

Please provide a clear and concise answer, citing specific information from the context when possible."""

        # Initialize LangChain OpenAI instance
        llm = ChatOpenAI(api_key=api_key, temperature=0.5)

        # Generate response with context
        ai_message = llm.invoke(prompt)

        # Extract the content of the AIMessage
        if hasattr(ai_message, "content"):
            response_text = ai_message.content
        else:
            raise ValueError("Unexpected response format from LangChain.")

        return func.HttpResponse(
            response_text,
            status_code=200,
            headers=cors_headers
        )

    except Exception as e:
        logging.error(f"Error in autocomplete: {e}")
        return func.HttpResponse(
            f"An error occurred during processing: {str(e)}",
            status_code=500,
            headers=cors_headers
        )