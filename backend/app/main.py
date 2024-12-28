# main.py
import azure.functions as func
from dotenv import load_dotenv
import os
from app.routes.upload_document import upload_document
from app.services.blob_service import get_blob_service_client

# Load environment variables
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
blob_service_client = get_blob_service_client(connection_string)

# Register Routes
@app.route(route="UploadDocument", auth_level=func.AuthLevel.ANONYMOUS)
def upload_document_route(req: func.HttpRequest) -> func.HttpResponse:
    return upload_document(req, blob_service_client, blob_container_name)
