# routes/autocomplete.py
import logging
import azure.functions as func
from app.utils.cors import cors_headers
from langchain_openai import ChatOpenAI
import os

def autocomplete(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Processing autocomplete request.")

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

        # Fetch the OpenAI API key from environment variables
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables.")

        # Initialize LangChain OpenAI instance
        llm = ChatOpenAI(api_key=api_key, temperature=0.5)

        # Generate response
        ai_message = llm.invoke(query)

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
            "An error occurred during processing.",
            status_code=500,
            headers=cors_headers
        )
