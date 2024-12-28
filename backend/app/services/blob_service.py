# services/blob_service.py
from azure.storage.blob import BlobServiceClient
import logging

def get_blob_service_client(connection_string):
    return BlobServiceClient.from_connection_string(connection_string)

def get_blob_url_with_content_type(blob_client, mime_type):
    """Get blob URL with appropriate content type headers"""
    # Get the base URL
    url = blob_client.url

    # For PDFs, add a query parameter to indicate inline content disposition
    if mime_type == 'application/pdf':
        # Add response-content-type and response-content-disposition query parameters
        separator = '&' if '?' in url else '?'
        url = f"{url}{separator}response-content-type=application/pdf&response-content-disposition=inline"

    return url

def upload_to_blob(container_client, file_name, file_content, mime_type):
    """
    Upload file to blob storage with appropriate content settings
    """
    # Ensure the container exists
    if not container_client.exists():
        logging.info(f"Creating container: {container_client.container_name}")
        container_client.create_container()

    # Get blob client
    blob_client = container_client.get_blob_client(file_name)

    # Create BlobProperties object for content settings
    from azure.storage.blob import ContentSettings

    content_settings = ContentSettings(
        content_type=mime_type,
        content_disposition='inline' if mime_type == 'application/pdf' else f'attachment; filename="{file_name}"'
    )

    # Upload the file with content settings
    blob_client.upload_blob(data=file_content, overwrite=True, content_settings=content_settings)

    # Get URL with appropriate query parameters
    url = get_blob_url_with_content_type(blob_client, mime_type)

    logging.info(f"Uploaded file: {file_name} to container: {container_client.container_name}")

    return url