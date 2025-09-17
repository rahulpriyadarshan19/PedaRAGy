# app/vector_store/search.py

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .pinecone_client import PineconeClient
from app.embeddings.embedding_model import EmbeddingModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SemanticSearch:
    """
    Semantic search functionality using Pinecone vector database and embeddings.
    """
    
    def __init__(self, index_name: str = "pedaragy-documents", 
                 embedding_model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize semantic search.
        
        Args:
            index_name: Name of the Pinecone index to use
            embedding_model_name: Name of the embedding model to use
        """
        self.index_name = index_name
        self.pinecone_client = PineconeClient()
        self.embedding_model = EmbeddingModel(embedding_model_name)
        
        # Connect to or create the index
        if not self.pinecone_client.connect_to_index(index_name):
            if not self.pinecone_client.create_index(index_name, dimension=384):
                raise RuntimeError(f"Failed to create or connect to index '{index_name}'")
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]],
                     namespace: str = "default") -> bool:
        """
        Add documents to the vector database.
        
        Args:
            documents: List of documents with 'text' and optional metadata
            namespace: Namespace to store documents in
            
        Returns:
            bool: True if documents were added successfully
        """
        try:
            # Upsert documents with embeddings
            success = self.pinecone_client.upsert_documents(documents, embeddings, namespace=namespace)
            
            if success:
                logger.info(f"Added {len(documents)} documents to namespace '{namespace}'")
            
            return success
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False
    
    def search(self, query: str, top_k: int = 3, namespace: str = "default",
               filter_dict: Optional[Dict] = None, min_score: float = 0.0) -> List[Dict[str, Any]]:
        """
        Perform semantic search for documents similar to the query.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            namespace: Namespace to search in
            filter_dict: Optional metadata filter
            min_score: Minimum similarity score threshold
            
        Returns:
            List of search results with enhanced metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.embed_text(query)
            
            # Search in Pinecone
            results = self.pinecone_client.search(
                query_vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter_dict=filter_dict
            )
            
            # Filter by minimum score and enhance results
            enhanced_results = []
            for result in results:
                if result['score'] >= min_score:
                    enhanced_result = {
                        'id': result['id'],
                        'score': result['score'],
                        'text': result['metadata'].get('text', ''),
                        'metadata': result['metadata'],
                        'relevance_percentage': round(result['score'] * 100, 2)
                    }
                    enhanced_results.append(enhanced_result)
            
            logger.info(f"Found {len(enhanced_results)} results for query: '{query}'")
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            return []
    
    def search_by_source(self, query: str, source: str, top_k: int = 5,
                        namespace: str = "default") -> List[Dict[str, Any]]:
        """
        Search for documents from a specific source.
        
        Args:
            query: Search query text
            source: Source file name to filter by
            top_k: Number of results to return
            namespace: Namespace to search in
            
        Returns:
            List of search results from the specified source
        """
        filter_dict = {"source": {"$eq": source}}
        return self.search(query, top_k, namespace, filter_dict)
    
    def search_by_date_range(self, query: str, start_date: str, end_date: str,
                           top_k: int = 5, namespace: str = "default") -> List[Dict[str, Any]]:
        """
        Search for documents within a date range.
        
        Args:
            query: Search query text
            start_date: Start date in ISO format (YYYY-MM-DD)
            end_date: End date in ISO format (YYYY-MM-DD)
            top_k: Number of results to return
            namespace: Namespace to search in
            
        Returns:
            List of search results within the date range
        """
        filter_dict = {
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }
        return self.search(query, top_k, namespace, filter_dict)
    
    def get_document_by_id(self, doc_id: str, namespace: str = "default") -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by its ID.
        
        Args:
            doc_id: Document ID to retrieve
            namespace: Namespace to search in
            
        Returns:
            Document data if found, None otherwise
        """
        try:
            results = self.pinecone_client.search(
                query_vector=[0.0] * 384,  # Dummy vector
                top_k=1,
                namespace=namespace,
                filter_dict={"id": {"$eq": doc_id}}
            )
            
            if results:
                result = results[0]
                return {
                    'id': result['id'],
                    'text': result['metadata'].get('text', ''),
                    'metadata': result['metadata']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving document {doc_id}: {e}")
            return None
    
    def delete_document(self, doc_id: str, namespace: str = "default") -> bool:
        """
        Delete a document by its ID.
        
        Args:
            doc_id: Document ID to delete
            namespace: Namespace to delete from
            
        Returns:
            bool: True if deletion successful
        """
        return self.pinecone_client.delete_vectors([doc_id], namespace)
    
    def get_index_statistics(self, namespace: str = "default") -> Dict[str, Any]:
        """
        Get statistics about the search index.
        
        Args:
            namespace: Namespace to get stats for
            
        Returns:
            Dictionary with index statistics
        """
        return self.pinecone_client.get_index_stats(namespace)
    
    def export_search_results(self, results: List[Dict[str, Any]], 
                            filename: str = None) -> str:
        """
        Export search results to a JSON file.
        
        Args:
            results: Search results to export
            filename: Output filename (optional)
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Search results exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting results: {e}")
            return ""

# Example usage and testing functions
def example_usage():
    """
    Example usage of SemanticSearch.
    """
    # Initialize search
    search = SemanticSearch()
    
    # Example documents to add
    documents = [
        {
            "id": "ml_intro",
            "text": "Machine learning is a method of data analysis that automates analytical model building. It is a branch of artificial intelligence based on the idea that systems can learn from data, identify patterns and make decisions with minimal human intervention.",
            "metadata": {
                "source": "ml_guide.pdf",
                "page": 1,
                "category": "introduction",
                "author": "AI Research Team"
            }
        },
        {
            "id": "nlp_basics",
            "text": "Natural Language Processing (NLP) is a subfield of linguistics, computer science, and artificial intelligence concerned with the interactions between computers and human language, in particular how to program computers to process and analyze large amounts of natural language data.",
            "metadata": {
                "source": "nlp_guide.pdf",
                "page": 1,
                "category": "basics",
                "author": "NLP Research Team"
            }
        },
        {
            "id": "vector_db_concept",
            "text": "Vector databases are specialized databases designed to store, index, and query high-dimensional vectors efficiently. They are essential for applications involving machine learning, semantic search, and similarity matching.",
            "metadata": {
                "source": "vector_db_guide.pdf",
                "page": 1,
                "category": "concepts",
                "author": "Database Research Team"
            }
        },
        {
            "id": "embedding_techniques",
            "text": "Embeddings are dense vector representations of text, images, or other data types that capture semantic meaning. Popular embedding techniques include Word2Vec, GloVe, BERT, and Sentence Transformers.",
            "metadata": {
                "source": "embedding_guide.pdf",
                "page": 1,
                "category": "techniques",
                "author": "Embedding Research Team"
            }
        }
    ]
    
    # Add documents to the search index
    print("Adding documents to search index...")
    if search.add_documents(documents):
        print("Documents added successfully!")
    
    # Perform various searches
    queries = [
        "What is machine learning?",
        "How do computers understand language?",
        "What are vector databases used for?",
        "Tell me about text embeddings"
    ]
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Search Query: '{query}'")
        print('='*60)
        
        results = search.search(query, top_k=3, min_score=0.3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Relevance: {result['relevance_percentage']}%")
                print(f"   Document ID: {result['id']}")
                print(f"   Source: {result['metadata'].get('source', 'Unknown')}")
                print(f"   Category: {result['metadata'].get('category', 'Unknown')}")
                print(f"   Text: {result['text'][:200]}...")
        else:
            print("No relevant results found.")
    
    # Search by source
    print(f"\n{'='*60}")
    print("Searching only in 'ml_guide.pdf':")
    print('='*60)
    
    ml_results = search.search_by_source("artificial intelligence", "ml_guide.pdf", top_k=2)
    for result in ml_results:
        print(f"Source: {result['metadata']['source']}")
        print(f"Text: {result['text'][:150]}...")
        print()
    
    # Get index statistics
    print(f"\n{'='*60}")
    print("Index Statistics:")
    print('='*60)
    
    stats = search.get_index_statistics()
    print(f"Total vectors: {stats.get('total_vector_count', 0)}")
    print(f"Namespaces: {list(stats.get('namespaces', {}).keys())}")
    
    # Export results
    all_results = search.search("machine learning and AI", top_k=5)
    if all_results:
        export_file = search.export_search_results(all_results, "example_search_results.json")
        print(f"\nResults exported to: {export_file}")

def test_search_functionality():
    """
    Test various search functionalities.
    """
    search = SemanticSearch()
    
    # Test queries with different types
    test_cases = [
        {
            "query": "machine learning algorithms",
            "description": "Technical query about ML"
        },
        {
            "query": "how to process text data",
            "description": "Practical application query"
        },
        {
            "query": "database storage optimization",
            "description": "System performance query"
        }
    ]
    
    print("Testing search functionality...")
    for test_case in test_cases:
        print(f"\nTest: {test_case['description']}")
        print(f"Query: '{test_case['query']}'")
        
        results = search.search(test_case['query'], top_k=2, min_score=0.2)
        print(f"Results found: {len(results)}")
        
        for result in results:
            print(f"  - {result['relevance_percentage']}%: {result['metadata'].get('source', 'Unknown')}")

if __name__ == "__main__":
    # Run examples if script is executed directly
    print("Running SemanticSearch examples...")
    example_usage()
    
    print("\n" + "="*80)
    print("Running search functionality tests...")
    test_search_functionality()
