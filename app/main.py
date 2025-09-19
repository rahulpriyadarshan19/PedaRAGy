import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from app.embeddings.embedding_model import EmbeddingModel
from app.vector_store.search import SemanticSearch
from app.preprocessing.chunker import Chunker
from app.vector_store.pinecone_client import PineconeClient
from app.ingestion.pdf_extractor import PDFExtractor
import sys
import os
from app.llm.ollama_client import return_response

load_dotenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")

embedding_model = EmbeddingModel()
semantic_search = SemanticSearch()
chunker = Chunker()
pinecone_client = PineconeClient(api_key=pinecone_api_key)
pdf_extractor = PDFExtractor()
app = FastAPI()


class FilePathRequest(BaseModel):
    file_path: str

class AskRequest(BaseModel):
    prompt: str
    model: str = "codegemma:7b"


@app.get("/")
def root():
    return {"message": "Welcome to PedaRAGy API", "endpoints": ["/add_file/", "/ask/", "/docs"]}

@app.post("/ask/")
def ask_prompt(request: AskRequest):
    prompt = request.prompt
    model = request.model
    
    # 1. Search vector store for relevant chunks (same as search endpoint)
    relevant_chunks = semantic_search.search(prompt)
    # 2. Get context from relevant chunks
    context = "\n\n".join([doc.get('text', '') for doc in relevant_chunks])
    
    # # 3. Limit context to 1500 tokens (approximately 6000 characters)
    # max_context_chars = 6000  # 1500 tokens * 4 chars/token
    # if len(context) > max_context_chars:
    #     context = context[:max_context_chars] + "..."
    
    # 4. Send query to LLM with context
    llm_response = return_response(f"Context: {context}\n\nQuestion: {prompt}", model=model)
    # 5. Return LLM response
    return {"answer": llm_response}
    


@app.post("/add_data/")
def add_file(request: FilePathRequest):
    """Add a file to the vector store.

    Parameters
    ----------
    request : FilePathRequest
        The request containing the file path to add to the vector store.
    """
    
    file_path = request.file_path
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Extract text from file
    extracted_data = pdf_extractor.extract_text(file_path, include_metadata=True)
    text = extracted_data['text']
    pdf_metadata = extracted_data['pdf_metadata']
    
    # Read file, chunk text
    # with open(file_path, "r") as file:
    #     text = file.read()
    chunks = chunker.chunk_by_chapter(text)
    
    # Convert to documents with enriched metadata
    documents = []
    for i, chunk in enumerate(chunks):
        documents.append({
            "id": f"{extracted_data["file_name"]}_{i}",
            "text": chunk,
            "metadata": {
                "chunk_index": i,
                "chunk_method": "chapter",
                # File-level metadata
                "source": extracted_data["file_name"]
            }
        })
    
    # Check if pinecone index exists, if not create one
    if not pinecone_client.connect_to_index(semantic_search.index_name):
        try:
            pinecone_client.create_index(semantic_search.index_name, dimension=384)
        except Exception as e:
            raise RuntimeError(f"Failed to create index {semantic_search.index_name}: {e}")
    else:
        pinecone_client.connect_to_index(semantic_search.index_name)

    # Generate embeddings
    embeddings = embedding_model.embed_texts([document['text'] for document in documents])
    
    # Add text to vector store
    semantic_search.add_documents(documents, embeddings, namespace="default")
    return {"message": "Processed file, generated embeddings and added to vector store"}

@app.post("/search/")
def search(query: str):
    """Search the vector store for similar documents.
    """
    return semantic_search.search(query)
