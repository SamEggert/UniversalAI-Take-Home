from psycopg2 import connect, sql

def connect_to_db():
    return connect(
        dbname="your_db_name",
        user="your_username",
        password="your_password",
        host="your_host",
        port="your_port"
    )

def insert_embedding(document_name, embedding, metadata):
    with connect_to_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO document_embeddings (document_name, embedding, metadata)
                VALUES (%s, %s, %s)
                """,
                (document_name, embedding, metadata)
            )
            conn.commit()

def search_embeddings(query_embedding, top_k=5):
    with connect_to_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT document_name, metadata, embedding
                FROM document_embeddings
                ORDER BY embedding <-> %s
                LIMIT %s
                """,
                (query_embedding, top_k)
            )
            return cur.fetchall()
