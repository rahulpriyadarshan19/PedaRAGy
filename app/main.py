import os
from dotenv import load_dotenv
from fastapi import FastAPI
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
def add_file(file_path: str):
    """Add a file to the vector store.

    Parameters
    ----------
    file_path : str
        The path to the file to add to the vector store.
    """
    
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
                "source": extracted_data["file_name"],
                "file_size": extracted_data["file_size"],
                "page_count": extracted_data["page_count"],
                "extraction_timestamp": extracted_data["extraction_timestamp"],
                
                # PDF metadata
                "title": pdf_metadata.get("title", ""),
                "author": pdf_metadata.get("author", ""),
                "subject": pdf_metadata.get("subject", ""),
                "creation_date": pdf_metadata.get("creation_date", ""),
                "keywords": pdf_metadata.get("keywords", "")
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
