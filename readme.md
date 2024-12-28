# Document RAG System

A cloud-based document processing and query system using RAG (Retrieval-Augmented Generation) with chain-of-thought reasoning.

## Project Setup Tasks

### 1. Azure Resources Setup
- [x] Create Azure Resource Group
- [x] Create Azure Storage Account
- [x] Create Azure Cosmos DB instance for vector storage
- [x] Set up Azure OpenAI Service
- [x] Configure CORS settings for storage account
- [x] Generate SAS tokens for secure access

s
### 2. Backend Development (Python)
- [x] Initialize Azure Functions project structure
- [x] Set up Python virtual environment
- [x] Install required dependencies:
  - langchain
  - azure-functions
  - azure-storage-blob
  - azure-cosmos
  - openai
  - numpy
  - faiss-cpu
  - unstructured

#### Document Processing Pipeline
- [ ] Implement document upload handler
- [ ] Create document parsing logic
- [ ] Set up vector embeddings generation
- [ ] Implement vector storage in Cosmos DB
- [ ] Add error handling and logging

#### Query Processing Pipeline
- [ ] Implement RAG pipeline
- [ ] Add chain-of-thought reasoning
- [ ] Create query decomposition logic
- [ ] Add language detection
- [ ] Implement intent classification
- [ ] Set up document retrieval and reranking
- [ ] Add response generation with source citations

### 3. Frontend Development (React)
- [ ] Create new React project
- [ ] Set up project structure
- [ ] Install required dependencies:
  - @azure/storage-blob
  - @azure/identity
  - axios
  - tailwindcss

#### Components
- [ ] Create document upload interface
- [ ] Implement chat interface
- [ ] Add loading states and error handling
- [ ] Implement response rendering with citations
- [ ] Add progress indicators for uploads

### 4. Integration
- [ ] Connect frontend to Azure Blob Storage
- [ ] Set up API communication between frontend and Azure Functions
- [ ] Implement proper error handling
- [ ] Add request/response validation

### 5. Performance Optimization
- [ ] Optimize vector search performance
- [ ] Implement caching where appropriate
- [ ] Add batch processing for multiple documents
- [ ] Optimize API response times

### 6. Testing
- [ ] Write unit tests for backend functions
- [ ] Test with various document types
- [ ] Load testing for concurrent users
- [ ] Test RAG accuracy and relevance
- [ ] End-to-end testing

### 7. Documentation
- [ ] API documentation
- [ ] Setup instructions
- [ ] Usage examples
- [ ] Performance benchmarks

## Getting Started

1. Clone this repository
2. Set up Azure resources following the setup guide
3. Configure environment variables
4. Install dependencies for both frontend and backend
5. Run the development servers

## Environment Variables

Backend (.env):
```
AZURE_STORAGE_CONNECTION_STRING=
AZURE_COSMOS_CONNECTION_STRING=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_ENDPOINT=
```

Frontend (.env):
```
REACT_APP_STORAGE_ACCOUNT_NAME=
REACT_APP_SAS_TOKEN=
REACT_APP_API_ENDPOINT=
```