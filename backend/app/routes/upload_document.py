import logging
import azure.functions as func
from app.utils.cors import cors_headers
from app.services.blob_service import get_blob_service_client, upload_to_blob
from openai import OpenAI
import json
import os
import tiktoken
import psycopg2
from psycopg2.extras import Json

def generate_embedding(text, model="text-embedding-3-small"):
    """
    Generate an embedding for the given text using OpenAI's embedding API.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding

def count_tokens(text, encoding_name="cl100k_base"):
    """
    Count the number of tokens in a text string using tiktoken.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))

def upload_document(req: func.HttpRequest, blob_service_client, blob_container_name) -> func.HttpResponse:
    logging.info("Processing upload document request.")

    # Handle preflight (OPTIONS) requests for CORS
    if req.method == 'OPTIONS':
        return func.HttpResponse(status_code=200, headers=cors_headers)

    try:
        # Parse the uploaded file
        uploaded_file = req.files.get('file')
        if not uploaded_file:
            return func.HttpResponse(
                "No file provided in the request.",
                status_code=400,
                headers=cors_headers
            )

        file_name = uploaded_file.filename
        file_content = uploaded_file.stream.read()
        text_content = file_content.decode('utf-8')  # Assuming the file is text-based

        # Check token count
        token_count = count_tokens(text_content)
        if token_count > 8191:  # text-embedding-3-small/large max token limit
            return func.HttpResponse(
                f"File exceeds the token limit (8191 tokens). Current token count: {token_count}",
                status_code=400,
                headers=cors_headers
            )

        # Generate embedding for the file content
        embedding = generate_embedding(text_content)

        # Save the file to Blob Storage
        container_client = blob_service_client.get_container_client(blob_container_name)
        upload_to_blob(container_client, file_name, file_content)

        # Prepare metadata
        metadata = {
            "file_name": file_name,
            "file_size": len(file_content),
            "token_count": token_count,
            "embedding_generated": True,
            "embedding_model": "text-embedding-3-small",
            "embedding_dimensions": len(embedding)
        }

        # Store the embedding in the database
        try:
            with psycopg2.connect(
                dbname=os.getenv("PGDATABASE"),
                user=os.getenv("PGUSER"),
                password=os.getenv("PGPASSWORD"),
                host=os.getenv("PGHOST"),
                port=os.getenv("PGPORT")
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO document_embeddings (document_name, embedding, metadata)
                        VALUES (%s, %s, %s)
                        """,
                        (file_name, embedding, Json(metadata))
                    )
                    conn.commit()
        except Exception as db_error:
            logging.error(f"Database error: {db_error}")
            return func.HttpResponse(
                "Error storing document embedding in database.",
                status_code=500,
                headers=cors_headers
            )

        # Return success response
        return func.HttpResponse(
            json.dumps({
                "message": f"File '{file_name}' uploaded successfully.",
                "metadata": metadata
            }),
            status_code=200,
            headers={**cors_headers, "Content-Type": "application/json"}
        )

    except Exception as e:
        logging.error(f"Error processing the upload: {e}")
        return func.HttpResponse(
            "An error occurred during file upload.",
            status_code=500,
            headers=cors_headers
        )