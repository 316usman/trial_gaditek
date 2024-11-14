# FastAPI RAG Bot

This is a FastAPI application for processing various types of documents, including PDFs, DOCX, and PPTX files. The application provides multiple endpoints for uploading files, extracting their text, chunking the extracted text, and querying the stored document chunks for relevant information. It integrates with OpenAI's embeddings to enhance document search functionality.

## Features

- **Upload Files**: Upload multiple files (PDF, DOCX, PPTX, etc.) and extract text from them.
- **Text Extraction**: Extract text from supported file formats (PDF, DOCX, TXT, PPTX).
- **Chunking**: Split extracted text into chunks for efficient search and retrieval.
- **Search**: Search for specific text queries and retrieve relevant document chunks.
- **File Text Retrieval**: Retrieve the full extracted text of a document.
- **Embedding & Querying**: Generate embeddings for document text and query against those embeddings using Faiss In-memory vector Store

## Requirements

- Python 3.11.4
- FastAPI
- Uvicorn (for serving the app)
- Requests (for downloading files)
- Python-Magic (for file type detection)
- Langchain (for text splitting)
- Faiss (for vector search)
- OpenAI (for generating embeddings and responses)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/fastapi-document-processor.git
    cd fastapi-document-processor
    ```

2. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up the environment variables (create a `.env` file):

    ```bash
    OPENAI_API_KEY=your-openai-api-key
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata/
    ```

    Make sure to replace `your-openai-api-key` with your actual OpenAI API key.

4. Run the FastAPI application:

    ```bash
    uvicorn app.main:app --reload
    ```

## Postman Collection

A Postman collection is provided for easy testing of the API endpoints. The collection includes pre-configured requests for all available API endpoints, allowing you to quickly interact with the application without manually creating requests.

### Import the Collection

1. Download the Postman collection file (e.g., `fastapi-document-processor.postman_collection.json`).
2. Open Postman and click on the **Import** button.
3. Select the downloaded collection file to import it into Postman.

The Postman collection includes the following requests:

- **Upload Files** (`POST /uploadfiles/`): Upload files and extract text from them.
- **Get Chunks** (`POST /getchunks/`): Get chunks for a specific query from the in-memory Faiss database.
- **Get Full Text** (`POST /getfulltext/`): Retrieve the full text of a file by its URL.
- **Get Response** (`POST /getresponse/`): Get a response for a query based on the extracted text chunks.

## API Endpoints

### `/uploadfiles/`
**POST**: Upload files and extract text from them.

- **Payload**:
    ```json
    {
        "user_id": "123",
        "files": [
            {"file_id": "1", "file_url": "https://example.com/file1.pdf"},
            {"file_id": "2", "file_url": "https://example.com/file2.docx"}
        ],
        "chunk_size": 128
    }
    ```

- **Response**:
    ```json
    [
        {
            "file_id": "1",
            "text": "Extracted text from file 1",
            "user_id": "123",
            "message": "file processed successfully"
        },
        {
            "file_id": "2",
            "text": "Extracted text from file 2",
            "user_id": "123",
            "message": "file processed successfully"
        }
    ]
    ```

### `/getchunks/`
**POST**: Get chunks for a specific query from the in-memory Faiss database.

- **Payload**:
    ```json
    {
        "text": "Your query text here",
        "limit": 5
    }
    ```

- **Response**:
    ```json
    {
        "query_text": "Your query text here",
        "chunks": [
            "Relevant chunk 1",
            "Relevant chunk 2"
        ]
    }
    ```

### `/getfulltext/`
**POST**: Retrieve the full text of a file by its URL.

- **Payload**:
    ```json
    {
        "file_url": "https://example.com/file1.pdf"
    }
    ```

- **Response**:
    ```json
    {
        "text": "Extracted full text from the file"
    }
    ```

### `/getresponse/`
**POST**: Get a response for a query based on the extracted text chunks.

- **Payload**:
    ```json
    {
        "query_text": "Your query text here"
    }
    ```

- **Response**:
    ```json
    {
        "response": "The response containing the relevant quote from the document."
    }
    ```

## File Types Supported

- PDF (`application/pdf`)
- DOCX (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`)
- PPTX (`application/vnd.openxmlformats-officedocument.presentationml.presentation`)
- TXT (`text/*`)

## Dependencies

- `fastapi`: Web framework for building APIs.
- `uvicorn`: ASGI server for FastAPI.
- `requests`: For downloading files from URLs.
- `python-magic`: For detecting MIME types of files.
- `langchain`: For text splitting and processing.
- `faiss`: For vector search.
- `openai`: For generating embeddings using OpenAI API.
- `nltk`: For natural language processing tasks.
