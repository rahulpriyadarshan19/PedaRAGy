import requests
import sys
from datetime import datetime

def return_response(prompt: str, model: str = "codegemma:7b", max_new_tokens: int = 512) -> str:
    """
    Generate text using Ollama LLM via CallOllama.
    
    Args:
        prompt: Input prompt for text generation
        max_new_tokens: Maximum number of new tokens to generate (ignored for Ollama)
        
    Returns:
        Generated text response
    """
    url = 'http://69.197.139.26:5000/generate'
    headers = {
        "Authorization": f"Bearer @#$#234RAIN##SHINE$$INTHE$$CLUB",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "model": model
    }
    
    try:
        print("🔄 Calling Ollama LLM...")
        response = requests.post(url, headers=headers, json=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully got response from Ollama")
            return result.get("text", "")
        else:
            print(f"❌ Ollama request failed with status {response.status_code}: {response.text}")
            raise Exception(f"Ollama request failed: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        raise Exception(f"Failed to connect to Ollama: {str(e)}")
