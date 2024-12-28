# services/blob_service.py
from azure.storage.blob import BlobServiceClient
import logging

def get_blob_service_client(connection_string):
    return BlobServiceClient.from_connection_string(connection_string)

def upload_to_blob(container_client, file_name, file_content):
    # Ensure the container exists
    if not container_client.exists():
        logging.info(f"Creating container: {container_client.container_name}")
        container_client.create_container()

    # Upload the file
    container_client.upload_blob(name=file_name, data=file_content, overwrite=True)
    logging.info(f"Uploaded file: {file_name} to container: {container_client.container_name}")
