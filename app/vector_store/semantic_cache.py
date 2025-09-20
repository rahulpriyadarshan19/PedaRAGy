import os
import hashlib
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.vector_store.pinecone_client import PineconeClient
from app.embeddings.embedding_model import EmbeddingModel

class SemanticCache:
    """
    Semantic cache implementation using Pinecone for storing and retrieving
    query-response pairs based on semantic similarity.
    """
    
    def __init__(self, api_key: str, similarity_threshold: float = 0.95):
        """
        Initialize semantic cache.
        
        Args:
            api_key: Pinecone API key
            similarity_threshold: Minimum similarity score to consider a match (0.0-1.0)
        """
        self.pinecone_client = PineconeClient(api_key=api_key)
        self.embedding_model = EmbeddingModel()
        self.similarity_threshold = similarity_threshold
        self.cache_index_name = "semantic-cache"
        
        # Create cache index if it doesn't exist
        self._ensure_cache_index()
    
    def _ensure_cache_index(self):
        """Ensure the cache index exists in Pinecone."""
        if not self.pinecone_client.connect_to_index(self.cache_index_name):
            try:
                self.pinecone_client.create_index(
                    self.cache_index_name, 
                    dimension=384,  # Same as your embedding model
                    metric="cosine"
                )
                # Connect to the newly created index
                self.pinecone_client.connect_to_index(self.cache_index_name)
                print(f"✅ Created semantic cache index: {self.cache_index_name}")
            except Exception as e:
                print(f"⚠️  Cache index might already exist: {e}")
        else:
            print(f"✅ Connected to existing cache index: {self.cache_index_name}")
    
    def _generate_query_hash(self, prompt: str, mode: str) -> str:
        """Generate a unique hash for the query."""
        content = f"{prompt}_{mode}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_cache_id(self, prompt: str, mode: str) -> str:
        """Generate a unique ID for the cache entry."""
        return f"cache_{self._generate_query_hash(prompt, mode)}"
    
    def get_cached_response(self, prompt: str, mode: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response if a similar query exists.
        
        Args:
            prompt: The user's question
            mode: The response mode (explain, quiz, hint)
            
        Returns:
            Cached response dict if found, None otherwise
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.embed_text(prompt)
            
            # Search for similar queries in cache
            results = self.pinecone_client.search(
                query_vector=query_embedding,
                top_k=1,
                namespace="default"
            )
            
            if results and len(results) > 0:
                match = results[0]
                similarity_score = match.get('score', 0)
                
                # Check if similarity is above threshold
                if similarity_score >= self.similarity_threshold:
                    metadata = match.get('metadata', {})
                    
                    # Verify mode matches (optional - you might want to cache across modes)
                    if metadata.get('mode') == mode:
                        print(f"🎯 Cache hit! Similarity: {similarity_score:.3f}")
                        return {
                            'context': metadata.get('context', ''),
                            'response': metadata.get('response', ''),
                            'similarity_score': similarity_score,
                            'cached_at': metadata.get('cached_at', ''),
                            'original_query': metadata.get('original_query', '')
                        }
                    else:
                        print(f"⚠️  Similar query found but different mode. Similarity: {similarity_score:.3f}")
                else:
                    print(f"📊 Similar query found but below threshold. Similarity: {similarity_score:.3f}")
            
            print("🔍 No suitable cache entry found")
            return None
            
        except Exception as e:
            print(f"❌ Error retrieving from cache: {e}")
            return None
    
    def store_response(self, prompt: str, mode: str, context: str, response: str) -> bool:
        """
        Store a query-response pair in the cache.
        
        Args:
            prompt: The user's question
            mode: The response mode
            context: The context used for the response
            response: The LLM response
            
        Returns:
            True if stored successfully, False otherwise
        """
        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.embed_text(prompt)
            
            # Create cache entry
            cache_id = self._generate_cache_id(prompt, mode)
            
            metadata = {
                'original_query': prompt,
                'mode': mode,
                'context': context,
                'response': response,
                'cached_at': datetime.now().isoformat(),
                'query_hash': self._generate_query_hash(prompt, mode)
            }
            
            # Store in Pinecone
            self.pinecone_client.upsert_vectors(
                vectors=[{
                    'id': cache_id,
                    'values': query_embedding,
                    'metadata': metadata
                }],
                namespace="default"
            )
            
            print(f"💾 Cached response for query: {prompt[:50]}...")
            return True
            
        except Exception as e:
            print(f"❌ Error storing in cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache."""
        try:
            stats = self.pinecone_client.describe_index(self.cache_index_name)
            return {
                'index_name': self.cache_index_name,
                'total_vectors': stats.get('total_vector_count', 0),
                'dimension': stats.get('dimension', 0),
                'metric': stats.get('metric', 'cosine'),
                'similarity_threshold': self.similarity_threshold
            }
        except Exception as e:
            return {'error': f"Could not retrieve cache stats: {e}"}
    
    def clear_cache(self) -> bool:
        """Clear all entries from the cache."""
        try:
            # Delete the index and recreate it
            self.pinecone_client.delete_index(self.cache_index_name)
            self._ensure_cache_index()
            print("🗑️  Cache cleared successfully")
            return True
        except Exception as e:
            print(f"❌ Error clearing cache: {e}")
            return False
