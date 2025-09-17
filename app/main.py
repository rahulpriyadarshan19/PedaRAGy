import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from app.embeddings.embedding_model import EmbeddingModel
from app.vector_store.search import SemanticSearch
from app.preprocessing.chunker import Chunker
from app.vector_store.pinecone_client import PineconeClient
from app.ingestion.pdf_extractor import PDFExtractor

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


@app.get("/")
def root():
    return {"message": "Welcome to PedaRAGy API", "endpoints": ["/add_file/", "/ask/", "/docs"]}

@app.post("/ask/")
def ask_prompt(prompt: str):
    # 1. Embed prompt.
    prompt_embedding = embedding_model.embed_text(prompt)
    # 2. Search vector store for similar prompts.
    similar_prompts = semantic_search.search(prompt_embedding)
    # 3. Return most similar prompt.
    return similar_prompts[0]


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
