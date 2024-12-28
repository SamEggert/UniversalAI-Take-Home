import azure.functions as func
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

# Initialize the FunctionApp
app = func.FunctionApp()

# Load Azure Storage connection string
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
if not connection_string:
    raise ValueError("Environment variable AZURE_STORAGE_CONNECTION_STRING is not set or empty.")

# Set Blob Container Name
blob_container_name = "documents"  # Replace with your container name

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

@app.route(route="UploadDocument", auth_level=func.AuthLevel.ANONYMOUS)
def UploadDocument(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        # Parse the uploaded file
        uploaded_file = req.files.get('file')
        if not uploaded_file:
            return func.HttpResponse("No file provided in the request.", status_code=400)

        file_name = uploaded_file.filename
        file_content = uploaded_file.stream.read()

        # Get the Blob Container Client
        container_client = blob_service_client.get_container_client(blob_container_name)

        # Ensure the container exists
        if not container_client.exists():
            logging.info(f"Creating container: {blob_container_name}")
            container_client.create_container()

        # Upload the file to Azure Blob Storage
        container_client.upload_blob(name=file_name, data=file_content, overwrite=True)
        logging.info(f"Uploaded file: {file_name} to container: {blob_container_name}")

        return func.HttpResponse(f"File '{file_name}' uploaded successfully.", status_code=200)

    except Exception as e:
        logging.error(f"Error processing the upload: {e}")
        return func.HttpResponse("An error occurred during file upload.", status_code=500)