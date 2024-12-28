import os
from dotenv import load_dotenv
from psycopg2 import connect, sql
from psycopg2.extras import Json
import logging

# Load environment variables from .env file
load_dotenv()

def connect_to_db():
    """
    Establishes connection to PostgreSQL database using environment variables.
    Returns a database connection object.
    """
    return connect(
        dbname=os.getenv('PGDATABASE'),
        user=os.getenv('PGUSER'),
        password=os.getenv('PGPASSWORD'),
        host=os.getenv('PGHOST'),
        port=os.getenv('PGPORT')
    )

def insert_embedding(document_name: str, embedding: list, metadata: dict):
    """
    Inserts document embedding and metadata into the database.
    Args:
        document_name (str): Name of the document
        embedding (list): Vector embedding of the document
        metadata (dict): Additional metadata about the document
    """
    try:
        # Log the incoming data types
        logging.info(f"Inserting embedding for {document_name}")
        logging.info(f"Metadata type: {type(metadata)}")
        logging.info(f"Embedding type: {type(embedding)}")

        with connect_to_db() as conn:
            with conn.cursor() as cur:
                # Convert metadata to JSON using psycopg2's Json adapter
                json_metadata = Json(metadata)

                # Cast the embedding list to a vector
                cur.execute(
                    """
                    INSERT INTO document_embeddings (document_name, embedding, metadata)
                    VALUES (%s, %s::vector, %s)
                    """,
                    (str(document_name), embedding, json_metadata)
                )
                conn.commit()

    except Exception as e:
        logging.error(f"Error in insert_embedding: {str(e)}")
        logging.error(f"Failed metadata: {metadata}")
        raise

def search_embeddings(query_embedding: list, top_k: int = 5):
    """
    Searches for similar embeddings in the database and prints relevant document names with distances.
    Args:
        query_embedding (list): Vector embedding to search against
        top_k (int): Number of results to return
    Returns:
        list: List of tuples containing (document_name, metadata, embedding)
    """
    try:
        with connect_to_db() as conn:
            with conn.cursor() as cur:
                logging.info(f"Searching for top {top_k} similar embeddings")
                cur.execute(
                    """
                    SELECT
                        id,
                        document_name,
                        metadata,
                        embedding,
                        embedding <-> %s::vector as distance
                    FROM document_embeddings
                    ORDER BY embedding <-> %s::vector
                    LIMIT %s
                    """,
                    (query_embedding, query_embedding, top_k)
                )
                results = cur.fetchall()

                # Log and print the relevant document names with distances
                logging.info(f"Found {len(results)} matching documents")
                print("\nMost relevant documents:")
                for i, (doc_id, doc_name, metadata, embedding, distance) in enumerate(results, 1):
                    print(f"{i}. [ID: {doc_id}] {doc_name:<40} Distance: {distance:.4f}")
                    logging.debug(f"Matched document: {doc_name} (ID: {doc_id}) with distance: {distance:.4f}")

                # Return only the original expected fields
                return [(doc_name, metadata, embedding) for _, doc_name, metadata, embedding, _ in results]
    except Exception as e:
        logging.error(f"Error in search_embeddings: {str(e)}")
        raise