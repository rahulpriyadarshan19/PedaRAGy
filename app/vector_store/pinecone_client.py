# app/vector_store/pinecone_client.py

import os
import uuid
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PineconeClient:
    """
    Pinecone vector database client for managing document embeddings.
    """
    
    def __init__(self, api_key: Optional[str] = None, environment: str = "gcp-starter"):
        """
        Initialize Pinecone client.
        
        Args:
            api_key: Pinecone API key (if None, will use PINECONE_API_KEY env var)
            environment: Pinecone environment (default: gcp-starter for free tier)
        """
        self.api_key = api_key or os.getenv("PINECONE_API_KEY")
        if not self.api_key:
            raise ValueError("Pinecone API key is required. Set PINECONE_API_KEY environment variable or pass api_key parameter.")
        
        self.environment = environment
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None
        
    def create_index(self, index_name: str, dimension: int = 384, metric: str = "cosine") -> bool:
        """
        Create a new Pinecone index.
        
        Args:
            index_name: Name of the index to create
            dimension: Vector dimension (384 for all-MiniLM-L6-v2)
            metric: Distance metric (cosine, euclidean, dotproduct)
            
        Returns:
            bool: True if index was created successfully
        """
        try:
            # Check if index already exists
            if index_name in self.pc.list_indexes().names():
                logger.info(f"Index '{index_name}' already exists")
                self.index = self.pc.Index(index_name)
                return True
            
            # Create new index
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric=metric,
                spec=ServerlessSpec(
                    cloud='aws',
                    region='us-east-1'
                )
            )
            
            # Wait for index to be ready
            logger.info(f"Creating index '{index_name}'...")
            while not self.pc.describe_index(index_name).status['ready']:
                import time
                time.sleep(1)
            
            self.index = self.pc.Index(index_name)
            logger.info(f"Index '{index_name}' created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return False
    
    def connect_to_index(self, index_name: str) -> bool:
        """
        Connect to an existing Pinecone index.
        
        Args:
            index_name: Name of the index to connect to
            
        Returns:
            bool: True if connection successful
        """
        try:
            if index_name not in self.pc.list_indexes().names():
                logger.error(f"Index '{index_name}' does not exist")
                return False
            
            self.index = self.pc.Index(index_name)
            logger.info(f"Connected to index '{index_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to index: {e}")
            return False
    
    def upsert_vectors(self, vectors: List[Dict[str, Any]], namespace: str = "default") -> bool:
        """
        Insert or update vectors in the index.
        
        Args:
            vectors: List of vectors with 'id', 'values', and optional 'metadata'
            namespace: Namespace to store vectors in
            
        Returns:
            bool: True if upsert successful
        """
        if not self.index:
            logger.error("No index connected. Call create_index() or connect_to_index() first.")
            return False
        
        try:
            # Add timestamp to metadata if not present
            for vector in vectors:
                if 'metadata' not in vector:
                    vector['metadata'] = {}
                if 'timestamp' not in vector['metadata']:
                    vector['metadata']['timestamp'] = datetime.now().isoformat()
            
            self.index.upsert(vectors=vectors, namespace=namespace)
            logger.info(f"Upserted {len(vectors)} vectors to namespace '{namespace}'")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting vectors: {e}")
            return False
    
    def upsert_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]], 
                        namespace: str = "default") -> bool:
        """
        Upsert documents with their embeddings.
        
        Args:
            documents: List of documents with 'text' and optional metadata
            embeddings: List of embedding vectors corresponding to documents
            namespace: Namespace to store vectors in
            
        Returns:
            bool: True if upsert successful
        """
        if len(documents) != len(embeddings):
            logger.error("Number of documents and embeddings must match")
            return False
        
        vectors = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            vector = {
                'id': doc.get('id', str(uuid.uuid4())),
                'values': embedding,
                'metadata': {
                    'text': doc['text'],
                    'timestamp': datetime.now().isoformat()
                }
            }
            
            # Add any additional metadata from document
            if 'metadata' in doc:
                vector['metadata'].update(doc['metadata'])
            
            vectors.append(vector)
        
        return self.upsert_vectors(vectors, namespace)
    
    def search(self, query_vector: List[float], top_k: int = 5, 
               namespace: str = "default", filter_dict: Optional[Dict] = None) -> List[Dict]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            namespace: Namespace to search in
            filter_dict: Optional metadata filter
            
        Returns:
            List of search results with 'id', 'score', and 'metadata'
        """
        if not self.index:
            logger.error("No index connected. Call create_index() or connect_to_index() first.")
            return []
        
        try:
            results = self.index.query(
                vector=query_vector,
                top_k=top_k,
                namespace=namespace,
                filter=filter_dict,
                include_metadata=True
            )
            
            return results['matches']
            
        except Exception as e:
            logger.error(f"Error searching vectors: {e}")
            return []
    
    def delete_vectors(self, vector_ids: List[str], namespace: str = "default") -> bool:
        """
        Delete vectors by their IDs.
        
        Args:
            vector_ids: List of vector IDs to delete
            namespace: Namespace to delete from
            
        Returns:
            bool: True if deletion successful
        """
        if not self.index:
            logger.error("No index connected. Call create_index() or connect_to_index() first.")
            return False
        
        try:
            self.index.delete(ids=vector_ids, namespace=namespace)
            logger.info(f"Deleted {len(vector_ids)} vectors from namespace '{namespace}'")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting vectors: {e}")
            return False
    
    def get_index_stats(self, namespace: str = "default") -> Dict[str, Any]:
        """
        Get statistics about the index.
        
        Args:
            namespace: Namespace to get stats for
            
        Returns:
            Dictionary with index statistics
        """
        if not self.index:
            logger.error("No index connected. Call create_index() or connect_to_index() first.")
            return {}
        
        try:
            stats = self.index.describe_index_stats()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting index stats: {e}")
            return {}
    
    def list_namespaces(self) -> List[str]:
        """
        List all namespaces in the current index.
        
        Returns:
            List of namespace names
        """
        if not self.index:
            logger.error("No index connected. Call create_index() or connect_to_index() first.")
            return []
        
        try:
            stats = self.index.describe_index_stats()
            return list(stats.get('namespaces', {}).keys())
            
        except Exception as e:
            logger.error(f"Error listing namespaces: {e}")
            return []

# Example usage and testing functions
def example_usage():
    """
    Example usage of PineconeClient.
    """
    # Initialize client (make sure to set PINECONE_API_KEY environment variable)
    client = PineconeClient()
    
    # Create or connect to an index
    index_name = "pedaragy-documents"
    if not client.create_index(index_name, dimension=384):
        if not client.connect_to_index(index_name):
            print("Failed to create or connect to index")
            return
    
    # Example documents
    documents = [
        {
            "id": "doc1",
            "text": "Machine learning is a subset of artificial intelligence.",
            "metadata": {"source": "ml_guide.pdf", "page": 1}
        },
        {
            "id": "doc2", 
            "text": "Natural language processing helps computers understand human language.",
            "metadata": {"source": "nlp_guide.pdf", "page": 1}
        },
        {
            "id": "doc3",
            "text": "Vector databases store and search high-dimensional embeddings efficiently.",
            "metadata": {"source": "vector_db_guide.pdf", "page": 1}
        }
    ]
    
    # Generate embeddings (you would use your EmbeddingModel here)
    from app.embeddings.embedding_model import EmbeddingModel
    embedding_model = EmbeddingModel()
    embeddings = embedding_model.embed_texts([doc["text"] for doc in documents])
    
    # Upsert documents
    if client.upsert_documents(documents, embeddings):
        print("Documents upserted successfully")
    
    # Search for similar documents
    query = "What is artificial intelligence?"
    query_embedding = embedding_model.embed_text(query)
    results = client.search(query_embedding, top_k=3)
    
    print(f"\nSearch results for: '{query}'")
    for i, result in enumerate(results, 1):
        print(f"{i}. Score: {result['score']:.4f}")
        print(f"   Text: {result['metadata']['text']}")
        print(f"   Source: {result['metadata'].get('source', 'Unknown')}")
        print()
    
    # Get index statistics
    stats = client.get_index_stats()
    print("Index Statistics:")
    print(f"Total vectors: {stats.get('total_vector_count', 0)}")
    print(f"Namespaces: {list(stats.get('namespaces', {}).keys())}")

if __name__ == "__main__":
    # Run example if script is executed directly
    example_usage()
