# routes/upload_document.py
import logging
import azure.functions as func
from typing import List, Dict, Any
import numpy as np
from openai import OpenAI
import tiktoken
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import PyPDF2
import io
import mimetypes
from app.services.vector_service import insert_embedding
from psycopg2.extras import Json
import json
from app.utils.cors import cors_headers
from app.services.blob_service import upload_to_blob

@dataclass
class DocumentChunk:
    content: str
    start_idx: int
    end_idx: int
    metadata: Dict[str, Any]

def prepare_metadata(file_name: str, mime_type: str, chunk: DocumentChunk, blob_url: str) -> dict:
    return {
        "file_name": file_name or "Unknown Document",
        "file_type": mime_type,
        "chunk_metadata": {
            "chunk_size": chunk.metadata.get("chunk_size", 0)
        },
        "start_idx": chunk.start_idx,
        "end_idx": chunk.end_idx,
        "blob_url": blob_url,
        "content": chunk.content
    }



class DocumentProcessor:
    def __init__(self, max_chunk_size: int = 900):
        self.max_chunk_size = max_chunk_size
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self.client = OpenAI()

    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text content from PDF file and clean up formatting."""
        pdf_text = ""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            for page in pdf_reader.pages:
                # Extract text from page
                page_text = page.extract_text()

                # Clean up the text:
                # 1. Replace multiple newlines with a single one
                # 2. Replace multiple spaces with a single one
                # 3. Strip any leading/trailing whitespace
                cleaned_text = ' '.join(
                    line.strip()
                    for line in page_text.split('\n')
                    if line.strip()
                )

                pdf_text += cleaned_text + "\n"

        except Exception as e:
            logging.error(f"Error extracting PDF text: {str(e)}")
            raise Exception(f"Failed to process PDF: {str(e)}")

        # Final cleanup of the entire document
        cleaned_document = ' '.join(
            line.strip()
            for line in pdf_text.split('\n')
            if line.strip()
        )

        return cleaned_document.strip()

    def extract_text_from_file(self, file_content: bytes, mime_type: str) -> str:
        """Extract text based on file type."""
        if mime_type == 'application/pdf':
            return self.extract_text_from_pdf(file_content)
        elif mime_type.startswith('text/'):
            try:
                return file_content.decode('utf-8')
            except UnicodeDecodeError:
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        return file_content.decode(encoding)
                    except UnicodeDecodeError:
                        continue
                raise Exception("Unable to decode text file with supported encodings")
        else:
            raise Exception(f"Unsupported file type: {mime_type}")

    def chunk_document(self, text: str) -> List[DocumentChunk]:
        """Split document into chunks optimized for embedding."""
        tokens = self.encoding.encode(text)
        chunks = []

        current_chunk = []
        current_length = 0

        for i, token in enumerate(tokens):
            current_chunk.append(token)
            current_length += 1

            if current_length >= self.max_chunk_size:
                chunk_text = self.encoding.decode(current_chunk)
                chunks.append(DocumentChunk(
                    content=chunk_text,
                    start_idx=i - current_length + 1,
                    end_idx=i,
                    metadata={"chunk_size": current_length}
                ))
                current_chunk = []
                current_length = 0

        if current_chunk:
            chunk_text = self.encoding.decode(current_chunk)
            chunks.append(DocumentChunk(
                content=chunk_text,
                start_idx=len(tokens) - current_length,
                end_idx=len(tokens),
                metadata={"chunk_size": current_length}
            ))

        return chunks

    def generate_embeddings(self, chunks: List[DocumentChunk]) -> List[np.ndarray]:
        """Generate embeddings for chunks."""
        embeddings = []
        for chunk in chunks:
            response = self.client.embeddings.create(
                input=chunk.content,
                model="text-embedding-3-small"
            )
            embeddings.append(np.array(response.data[0].embedding))
        return embeddings

def upload_document(req: func.HttpRequest, blob_service_client, blob_container_name) -> func.HttpResponse:
    # Handle CORS preflight
    if req.method == 'OPTIONS':
        return func.HttpResponse(status_code=200, headers=cors_headers)

    try:
        # Initialize document processor
        processor = DocumentProcessor()

        # Get file content
        file = req.files.get('file')
        if not file:
            return func.HttpResponse(
                "No file provided",
                status_code=400,
                headers=cors_headers
            )

        file_content = file.read()
        file_name = file.filename

        # Determine file type
        mime_type, _ = mimetypes.guess_type(file_name)
        if not mime_type:
            mime_type = 'application/octet-stream'

        logging.info(f"Processing file {file_name} of type {mime_type}")

        # Save to blob storage with proper content settings
        container_client = blob_service_client.get_container_client(blob_container_name)
        blob_url = upload_to_blob(container_client, file_name, file_content, mime_type)

        try:
            # Extract text content based on file type
            text_content = processor.extract_text_from_file(file_content, mime_type)
        except Exception as e:
            logging.error(f"Text extraction error: {str(e)}")
            return func.HttpResponse(
                f"Error extracting text from file: {str(e)}",
                status_code=400,
                headers=cors_headers
            )

        if not text_content.strip():
            return func.HttpResponse(
                "No text content could be extracted from the file",
                status_code=400,
                headers=cors_headers
            )

        # Process document in chunks
        chunks = processor.chunk_document(text_content)
        logging.info(f"Created {len(chunks)} chunks from document")

        # Generate embeddings
        embeddings = processor.generate_embeddings(chunks)
        logging.info(f"Generated {len(embeddings)} embeddings")

        # Store chunks and embeddings
        failed_chunks = []
        with ThreadPoolExecutor() as executor:
            futures = []
            for chunk_idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                try:
                    # Prepare metadata with explicit type conversion
                    metadata = prepare_metadata(
                        file_name=file_name,
                        mime_type=mime_type,
                        chunk=chunk,
                        blob_url=blob_url
                    )
                    logging.debug(f"Prepared metadata: {metadata}")

                    # Verify metadata is JSON serializable
                    json.dumps(metadata)

                    futures.append(
                        executor.submit(
                            insert_embedding,
                            document_name=file_name,
                            embedding=embedding.tolist(),
                            metadata=metadata
                        )
                    )
                except Exception as e:
                    logging.error(f"Error preparing chunk {chunk_idx}: {str(e)}")
                    failed_chunks.append(chunk_idx)

            # Wait for all database operations to complete
            for idx, future in enumerate(futures):
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error inserting chunk {idx}: {str(e)}")
                    failed_chunks.append(idx)

        if failed_chunks:
            logging.error(f"Failed to process chunks: {failed_chunks}")
            return func.HttpResponse(
                f"Document processed with {len(failed_chunks)} failed chunks",
                status_code=207,
                headers=cors_headers
            )

        return func.HttpResponse(
            f"Document {file_name} processed successfully",
            status_code=200,
            headers=cors_headers
        )

    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
        return func.HttpResponse(
            f"Error processing document: {str(e)}",
            status_code=500,
            headers=cors_headers
        )
