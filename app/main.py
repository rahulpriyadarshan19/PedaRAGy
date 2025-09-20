import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.embeddings.embedding_model import EmbeddingModel
from app.vector_store.search import SemanticSearch
from app.preprocessing.chunker import Chunker
from app.vector_store.pinecone_client import PineconeClient
from app.ingestion.pdf_extractor import PDFExtractor
from app.llm.ollama_client import return_response
from app.llm.prompts import EXPLAIN_PROMPT, QUIZ_PROMPT, HINT_PROMPT, generate_prompt
from app.vector_store.semantic_cache import SemanticCache

load_dotenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")

embedding_model = EmbeddingModel()
semantic_search = SemanticSearch()
chunker = Chunker()
pinecone_client = PineconeClient(api_key=pinecone_api_key)
pdf_extractor = PDFExtractor()
semantic_cache = SemanticCache(api_key=pinecone_api_key, similarity_threshold=0.95)
app = FastAPI()


class FilePathRequest(BaseModel):
    file_path: str

class MultipleFilesRequest(BaseModel):
    file_paths: list[str]

class AskRequest(BaseModel):
    prompt: str
    model: str = "codegemma:7b"
    mode: str = "explain"  # explain, quiz, hint


@app.get("/")
def root():
    return {"message": "Welcome to PedaRAGy API", "endpoints": ["/add_data/", "/ask/", "/search/", "/cache/stats", "/cache/clear", "/docs"]}

@app.post("/ask/")
def ask_prompt(request: AskRequest):
    prompt = request.prompt
    model = request.model
    mode = request.mode
    
    # 1. Check semantic cache first
    cached_result = semantic_cache.get_cached_response(prompt, mode)
    if cached_result:
        return {
            "answer": cached_result['response'],
            "mode": mode,
            "cached": True,
            "similarity_score": cached_result['similarity_score'],
            "original_query": cached_result['original_query']
        }
    
    # 2. Search vector store for relevant chunks (same as search endpoint)
    relevant_chunks = semantic_search.search(prompt)
    # 3. Get context from relevant chunks
    context = "\n\n".join([doc.get('text', '') for doc in relevant_chunks])
    
    # # 4. Limit context to 1500 tokens (approximately 6000 characters)
    # max_context_chars = 6000  # 1500 tokens * 4 chars/token
    # if len(context) > max_context_chars:
    #     context = context[:max_context_chars] + "..."
    
    # 5. Select prompt template based on mode
    if mode == "explain":
        formatted_prompt = generate_prompt(EXPLAIN_PROMPT, context, prompt)
    elif mode == "quiz":
        formatted_prompt = generate_prompt(QUIZ_PROMPT, context, prompt)
    elif mode == "hint":
        formatted_prompt = generate_prompt(HINT_PROMPT, context, prompt)
    else:
        # Default to simple context + question format
        formatted_prompt = f"Context: {context}\n\nQuestion: {prompt}"
    
    # 6. Send query to LLM with formatted prompt
    llm_response = return_response(formatted_prompt, model=model)
    
    # 7. Store in semantic cache for future use
    semantic_cache.store_response(prompt, mode, context, llm_response)
    
    # 8. Return LLM response
    return {"answer": llm_response, "mode": mode, "cached": False}
    


@app.post("/add_data/")
def add_file(request: MultipleFilesRequest):
    """Add multiple files to the vector store.

    Parameters
    ----------
    request : MultipleFilesRequest
        The request containing a list of file paths to add to the vector store.
    """
    
    file_paths = request.file_paths
    
    if not file_paths:
        raise HTTPException(status_code=400, detail="No file paths provided")
    
    # Validate all files exist
    missing_files = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        raise HTTPException(status_code=404, detail=f"Files not found: {missing_files}")
    
    # Check if pinecone index exists, if not create one
    if not pinecone_client.connect_to_index(semantic_search.index_name):
        try:
            pinecone_client.create_index(semantic_search.index_name, dimension=384)
        except Exception as e:
            raise RuntimeError(f"Failed to create index {semantic_search.index_name}: {e}")
    else:
        pinecone_client.connect_to_index(semantic_search.index_name)
    
    all_documents = []
    processed_files = []
    failed_files = []
    
    # Process each file
    for file_path in file_paths:
        try:
            print(f"Processing file: {file_path}")
            
            # Extract text from file
            extracted_data = pdf_extractor.extract_text(file_path, include_metadata=True)
            text = extracted_data['text']
            
            # Chunk text
            chunks = chunker.chunk_by_chapter(text)
            
            # Convert to documents with enriched metadata
            file_documents = []
            for i, chunk in enumerate(chunks):
                file_documents.append({
                    "id": f"{extracted_data['file_name']}_{i}",
                    "text": chunk,
                    "metadata": {
                        "chunk_index": i,
                        "chunk_method": "chapter",
                        "source": extracted_data["file_name"],
                        "file_path": file_path
                    }
                })
            
            all_documents.extend(file_documents)
            processed_files.append(file_path)
            print(f"✅ Successfully processed {file_path} - {len(file_documents)} chunks")
            
        except Exception as e:
            print(f"❌ Failed to process {file_path}: {str(e)}")
            failed_files.append({"file": file_path, "error": str(e)})
            continue
    
    if not all_documents:
        raise HTTPException(status_code=500, detail="No documents were successfully processed")
    
    # Generate embeddings for all documents
    print(f"Generating embeddings for {len(all_documents)} documents...")
    embeddings = embedding_model.embed_texts([document['text'] for document in all_documents])
    
    # Add all documents to vector store
    print("Adding documents to vector store...")
    semantic_search.add_documents(all_documents, embeddings, namespace="default")
    
    return {
        "message": f"Processed {len(processed_files)} files successfully",
        "processed_files": processed_files,
        "total_chunks": len(all_documents),
        "failed_files": failed_files if failed_files else None
    }

@app.post("/search/")
def search(query: str):
    """Search the vector store for similar documents.
    """
    return semantic_search.search(query)

@app.get("/cache/stats")
def get_cache_stats():
    """Get semantic cache statistics."""
    return semantic_cache.get_cache_stats()

@app.delete("/cache/clear")
def clear_cache():
    """Clear the semantic cache."""
    success = semantic_cache.clear_cache()
    return {"success": success, "message": "Cache cleared" if success else "Failed to clear cache"}
