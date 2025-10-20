"""
Ollama LLM Client
Handles communication with local Ollama service for chat, structured extraction,
and vision capabilities using Llama models.
"""

import logging
import json
import os
from typing import Dict, Any, Optional, List, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Client for Ollama LLM service.
    
    Provides:
    - Chat completions
    - Structured data extraction with JSON schema
    - Vision completions (Llama 3.2 Vision)
    - Streaming support
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
        vision_model: Optional[str] = None,
        timeout: int = 120
    ):
        """
        Initialize Ollama client.
        
        Args:
            host: Ollama host URL (default: from env or localhost:11434)
            model: Default model name (default: llama3.2)
            vision_model: Vision model name (default: llama3.2-vision)
            timeout: Request timeout in seconds
        """
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
        self.vision_model = vision_model or os.getenv("OLLAMA_VISION_MODEL", "llama3.2-vision")
        self.timeout = timeout
        
        # Setup session with retries
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        
        logger.info(f"Ollama client initialized: {self.host}")
    
    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            response = self.session.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """List available models"""
        try:
            response = self.session.get(f"{self.host}/api/tags", timeout=10)
            response.raise_for_status()
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Union[Dict[str, Any], Any]:
        """
        Send chat completion request.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (default: self.model)
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            stream: Whether to stream response
            
        Returns:
            Response dict or generator if streaming
        """
        model = model or self.model
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            response = self.session.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=self.timeout,
                stream=stream
            )
            response.raise_for_status()
            
            if stream:
                return self._stream_response(response)
            else:
                return response.json()
                
        except Exception as e:
            logger.error(f"Chat request failed: {e}")
            raise
    
    def completion(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Simple completion request.
        
        Args:
            prompt: Text prompt
            model: Model to use
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            
        Returns:
            Response dict
        """
        model = model or self.model
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        if max_tokens:
            payload["options"]["num_predict"] = max_tokens
        
        try:
            response = self.session.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Completion request failed: {e}")
            raise
    
    def structured_extraction(
        self,
        prompt: str,
        schema: Dict[str, Any],
        model: Optional[str] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Extract structured data according to JSON schema.
        
        Args:
            prompt: Extraction prompt
            schema: JSON schema describing expected output
            model: Model to use
            temperature: Lower temperature for more consistent output
            
        Returns:
            Extracted data as dict
        """
        # Enhance prompt with schema and JSON instructions
        enhanced_prompt = f"""{prompt}

Respond with ONLY a valid JSON object matching this schema:
{json.dumps(schema, indent=2)}

Requirements:
- Output must be valid JSON
- Follow the schema structure exactly
- Do not include explanations outside the JSON
- Use null for missing values

JSON output:"""
        
        result = self.completion(
            prompt=enhanced_prompt,
            model=model,
            temperature=temperature,
            max_tokens=2000
        )
        
        # Extract and parse JSON from response
        response_text = result.get("response", "")
        
        try:
            # Try to parse as-is
            data = json.loads(response_text)
            return data
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
            # Try to find JSON object in text
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
            
            logger.error(f"Failed to parse structured output: {response_text[:200]}")
            return {}
    
    def vision_completion(
        self,
        prompt: str,
        image_data: bytes,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Vision completion with image input.
        
        Args:
            prompt: Text prompt
            image_data: Image bytes (PNG, JPEG, etc.)
            model: Vision model to use
            
        Returns:
            Response dict with text analysis
        """
        import base64
        
        model = model or self.vision_model
        
        # Encode image to base64
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        payload = {
            "model": model,
            "prompt": prompt,
            "images": [image_b64],
            "stream": False
        }
        
        try:
            response = self.session.post(
                f"{self.host}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            # Normalize output
            return {
                "text": result.get("response", ""),
                "model": model,
                "metadata": result
            }
            
        except Exception as e:
            logger.error(f"Vision completion failed: {e}")
            raise
    
    def _stream_response(self, response):
        """Generator for streaming responses"""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    yield data
                except json.JSONDecodeError:
                    continue


def verify_ollama() -> Dict[str, Any]:
    """
    Verify Ollama installation and model availability.
    
    Returns:
        Dict with status and available models
    """
    client = OllamaClient()
    
    status = {
        "ollama_available": False,
        "models": [],
        "required_models": [],
        "missing_models": []
    }
    
    # Check service
    if not client.is_available():
        status["error"] = "Ollama service not available at " + client.host
        return status
    
    status["ollama_available"] = True
    
    # List models
    models = client.list_models()
    status["models"] = models
    
    # Check required models
    required = ["llama3.2", "llama3.2:latest"]
    optional = ["llama3.2-vision", "llama3.2-vision:latest"]
    
    for model in required:
        if any(model in m for m in models):
            status["required_models"].append(model)
        else:
            status["missing_models"].append(model)
    
    return status


# Convenience function
def chat_with_ollama(message: str, context: Optional[List[Dict]] = None) -> str:
    """
    Simple chat function.
    
    Args:
        message: User message
        context: Previous conversation messages
        
    Returns:
        Assistant response text
    """
    client = OllamaClient()
    
    messages = context or []
    messages.append({"role": "user", "content": message})
    
    result = client.chat(messages=messages)
    
    return result.get("message", {}).get("content", "")
