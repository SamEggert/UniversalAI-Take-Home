# cleanup_utility.py
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
import psycopg2
from psycopg2 import sql
import logging

# Load environment variables
load_dotenv()

def connect_to_db():
    """Establish database connection"""
    return psycopg2.connect(
        dbname=os.getenv('PGDATABASE'),
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD'),
        host=os.getenv('PGHOST'),
        port=os.getenv('PGPORT')
    )

def cleanup_storage_and_db():
    """Clean up both blob storage and database"""
    try:
        # 1. Clear Blob Storage
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("Azure Storage connection string not found in environment variables")

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_name = "documents"  # Replace with your container name if different

        try:
            container_client = blob_service_client.get_container_client(container_name)
            blobs = container_client.list_blobs()
            for blob in blobs:
                logging.info(f"Deleting blob: {blob.name}")
                container_client.delete_blob(blob.name)
            logging.info("All blobs deleted successfully")
        except Exception as e:
            logging.error(f"Error clearing blob storage: {str(e)}")
            raise

        # 2. Recreate Database Table
        with connect_to_db() as conn:
            with conn.cursor() as cur:
                # Drop existing table if it exists
                cur.execute("""
                    DROP TABLE IF EXISTS document_embeddings;
                """)

                # Recreate table with embeddings as the last column
                cur.execute("""
                    CREATE TABLE document_embeddings (
                        id SERIAL PRIMARY KEY,
                        document_name TEXT,
                        metadata JSONB,
                        embedding VECTOR(1536)
                    );
                """)

                # Create an index on document_name if needed
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_document_name
                    ON document_embeddings(document_name);
                """)

                conn.commit()
                logging.info("Database table recreated successfully")

        return "Cleanup completed successfully"

    except Exception as e:
        logging.error(f"Cleanup failed: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        result = cleanup_storage_and_db()
        print(result)
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")