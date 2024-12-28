# routes/upload_document.py
import logging
import azure.functions as func
from app.utils.cors import cors_headers
from app.services.blob_service import get_blob_service_client, upload_to_blob

def upload_document(req: func.HttpRequest, blob_service_client, blob_container_name) -> func.HttpResponse:
    logging.info("Processing upload document request.")

    # Handle preflight (OPTIONS) requests for CORS
    if req.method == 'OPTIONS':
        return func.HttpResponse(status_code=200, headers=cors_headers)

    try:
        # Parse the uploaded file
        uploaded_file = req.files.get('file')
        if not uploaded_file:
            return func.HttpResponse("No file provided in the request.", status_code=400, headers=cors_headers)

        file_name = uploaded_file.filename
        file_content = uploaded_file.stream.read()

        # Get the Blob Container Client
        container_client = blob_service_client.get_container_client(blob_container_name)

        # Upload the file
        upload_to_blob(container_client, file_name, file_content)

        return func.HttpResponse(f"File '{file_name}' uploaded successfully.", status_code=200, headers=cors_headers)

    except Exception as e:
        logging.error(f"Error processing the upload: {e}")
        return func.HttpResponse("An error occurred during file upload.", status_code=500, headers=cors_headers)
