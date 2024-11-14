from fastapi import APIRouter, Body, HTTPException ,Form, File, UploadFile
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
from pydantic import BaseModel, HttpUrl
import requests
import magic
import re
from .services import * 
import traceback
import logging

router = APIRouter()

class UploadFilesPayload(BaseModel):
    file_id: str
    user_id: str
    text: str
    embedding: List[float]

class GetQueryResponse(BaseModel):
    query_text: str
    chunks: List[str] 

class GetFileTextResponse(BaseModel):
    text: str

class TextRequest(BaseModel):
    query_text: str

class ChunkResponse(BaseModel):
    response: str

@router.post("/uploadfiles/", response_model=UploadFilesPayload)
async def upload_files(payload: Dict = Body(..., example={
    "user_id": "123",
    "files": [
        {"file_id": "1", "file_url": "https://example.com/file1.pdf"},
        {"file_id": "2", "file_url": "https://example.com/file2.docx"}
    ]
})):
    """
    Upload multiple files for text extraction.
    
    - **payload**: JSON object containing `user_id` and a list of `files`.
        - **user_id**: User identifier (string, required).
        - **files**: List of dictionaries containing `file_id` (string) and `file_url` (string) for each file to process (required).
            - Example:
                ```json
                {
                    "user_id": "123",
                    "files": [
                        {"file_id": "1", "file_url": "https://example.com/file1.pdf"},
                        {"file_id": "2", "file_url": "https://example.com/file2.docx"}
                    ],
                    chunk_size = 128
                }
                ```
    """
    user_id = payload.get("user_id")
    files = payload.get("files")
    chunk_size = payload.get("chunk_size", 128)
    
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not files:
        raise HTTPException(status_code=400, detail="files are required")
    embedded_chunks = []
    text_response = []
    for file in files:
        file_id = file.get("file_id")
        file_url = file.get("file_url")
        
        try:
            # Download the file
            response = requests.get(file_url)
            print ("Response Code",response.status_code)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to download file from {file_url}")
            
            content = response.content
            filename = file_url.split("/")[-1]
            
            # Determine the file type using python-magic
            mime = magic.Magic(mime=True)
            file_mime_type = mime.from_buffer(content)
            
            # Process the file based on its MIME type
            if file_mime_type == 'application/pdf':
                text_content = extract_whole_text_from_pdf(content)
            elif file_mime_type.startswith('text/'):
                text_content = extract_text_from_txt(content)
            elif file_mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                text_content = extract_text_from_docx(content)
            elif file_mime_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
                text_content = extract_text_from_pptx(content)
            else:
                text_content = None 
 
            text_response.append({
                "file_id": file_id,
                "text": text_content,
                "user_id": user_id,
                "message": "file processed successfully"
            })
            embedded_chunks.append(await process_documents_async(text_content, chunk_size=chunk_size))
            

        except Exception as e:
            embedded_chunks.append({
                "file_id": file_id,
                "file_url": file_url,
                "error": str(e)
            })
    
    return JSONResponse(content=embedded_chunks)

@router.post("/getchunks/", response_model=GetQueryResponse)
async def get_files(payload: Dict = Body(..., example={
    "text" : "text",

    })):
    """
    Get chunks for a specific query from the faiss in memory database.

    - **text**: Query text (string, required).
    - **limit**: Number of required Chunks
    """
    query_text = payload.get("text")
    limit = payload.get("limit")
    if not payload.get("text"):
        raise HTTPException(status_code=400, detail="text is required")
    try:
        query_embedding = np.array(get_openai_embeddings([query_text])[0]).reshape(1, -1)
        indices = search_vector(faiss_client, query_embedding)
        most_relevant_chunks = [text_list[i] for i in indices[0]]
        
        
        if not most_relevant_chunks:
            raise HTTPException(status_code=404, detail="No chunks found for the given user_id")

        return GetQueryResponse(query_text=query_text, chunks=most_relevant_chunks)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/getfulltext/", response_model=GetFileTextResponse)
async def get_file_text(
    payload: Dict = Body(..., example={
        "file_url": "https://www.filedomain.com/filename.pdf"
    })
):
    """
    Get the full text of a file.

    - **file**: File to process (optional).
    """
    file_url = payload.get("file_url")

    if not file_url:
        raise HTTPException(status_code=400, detail="Either file_url or file is required")

    try:
        if file_url:
            # Download the file
            response = requests.get(file_url)
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to download file from {file_url}")
            content = response.content
        else:
            content = await file.read()

        # Determine the file type using python-magic
        mime = magic.Magic(mime=True)
        file_mime_type = mime.from_buffer(content)

        # Process the file based on its MIME type
        if file_mime_type == 'application/pdf':
            text_content = extract_whole_text_from_pdf(content)
        elif file_mime_type.startswith('text/'):
            text_content = extract_text_from_txt(content)
        elif file_mime_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            text_content = extract_text_from_docx(content)
        elif file_mime_type == 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
            text_content = extract_text_from_pptx(content)
        else:
            text_content = None

        if text_content is None:
            raise HTTPException(status_code=400, detail="Unsupported file type")

        return GetFileTextResponse(text=text_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.post("/getresponse/", response_model=ChunkResponse)
async def search_chunks(request: TextRequest):
    query_text = request.query_text
    try:
        logging.info(f"Querying: query_text={query_text}")

        if not query_text:
            raise HTTPException(status_code=400, detail="query_text is required")

        query_embedding = np.array(get_openai_embeddings([query_text])[0]).reshape(1, -1)
        indices = search_vector(faiss_client, query_embedding)
        most_relevant_chunks = [text_list[i] for i in indices[0]]
        relevant_text = '\n'.join([chunk for chunk in most_relevant_chunks])
        answer =  get_openai_response(query_text, relevant_text)

        if not isinstance(answer, str) or not re.search(r'\*\*\*(.*?)\*\*\*', answer):
            print (answer)
            raise HTTPException(status_code=400, detail="No text found within text to quote.")
        
        response = ChunkResponse(response=answer)
        logging.info(f"Response created successfully: {response}")
        return response

    except HTTPException as e:
        logging.error(f"HTTP Exception: {str(e)}")
        raise e

    except Exception as e:
        logging.error(f"Unhandled exception: {str(e)}")
        logging.error(traceback.format_exc())  # Log the full traceback
        raise HTTPException(status_code=500, detail="Internal Server Error")
