import requests
from log import logger

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        self.base_url = base_url
        self.model = model
        self.timeout = 30
    
    def generate(self, prompt: str) -> str:
        """Direct API call to Ollama with explicit error handling"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
            
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            raise Exception("LLM request timeout")
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama server")
            raise Exception("LLM service unavailable")
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise
