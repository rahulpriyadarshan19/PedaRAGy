import os
import requests
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class HuggingFaceClient:
    """
    Client for interacting with Hugging Face Inference API for Gemma 7B model.
    """
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Hugging Face client.
        
        Args:
            api_token: Hugging Face API token. If None, will try to get from environment.
        """
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.api_token:
            raise ValueError("Hugging Face API token is required. Set HUGGINGFACE_API_TOKEN environment variable.")
        
        self.base_url = "https://api-inference.huggingface.co/models/google/gemma-7b-it"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def generate_text(self, prompt: str, max_new_tokens: int = 512, temperature: float = 0.7, 
                     top_p: float = 0.9, do_sample: bool = True) -> str:
        """
        Generate text using Gemma 7B model.
        
        Args:
            prompt: Input prompt for text generation
            max_new_tokens: Maximum number of new tokens to generate
            temperature: Sampling temperature (0.0 to 1.0)
            top_p: Top-p sampling parameter
            do_sample: Whether to use sampling
            
        Returns:
            Generated text response
        """
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "do_sample": do_sample,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    return result.get("generated_text", "")
                else:
                    return str(result)
            else:
                error_msg = f"API request failed with status {response.status_code}: {response.text}"
                raise Exception(error_msg)
                
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. The model might be loading.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def generate_with_context(self, context: str, question: str, max_new_tokens: int = 512) -> str:
        """
        Generate response with context and question format.
        
        Args:
            context: Context information
            question: Question to answer
            max_new_tokens: Maximum number of new tokens to generate
            
        Returns:
            Generated response
        """
        formatted_prompt = f"""Context: {context}

Question: {question}

Answer:"""
        
        return self.generate_text(formatted_prompt, max_new_tokens=max_new_tokens)
    
    def check_model_status(self) -> Dict[str, Any]:
        """
        Check if the model is loaded and ready.
        
        Returns:
            Status information about the model
        """
        try:
            response = requests.get(
                f"{self.base_url}/status",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": f"Status check failed: {response.status_code}"}
                
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Convenience function for backward compatibility
def return_response(prompt: str, max_new_tokens: int = 512) -> str:
    """
    Convenience function to generate text using Hugging Face Gemma 7B.
    
    Args:
        prompt: Input prompt
        max_new_tokens: Maximum number of new tokens to generate
        
    Returns:
        Generated text response
    """
    client = HuggingFaceClient()
    return client.generate_text(prompt, max_new_tokens=max_new_tokens)


# Example usage
if __name__ == "__main__":
    # Test the client
    try:
        client = HuggingFaceClient()
        
        # Check model status
        status = client.check_model_status()
        print(f"Model status: {status}")
        
        # Test text generation
        response = client.generate_text("What is machine learning?")
        print(f"Response: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
