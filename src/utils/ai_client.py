# AI Client configuration for Trend Micro RDSec AI Endpoint

import os
from typing import Optional, Dict, Any
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIClient:
    """
    Centralized AI client for Trend Micro RDSec AI Endpoint
    Provides chat models and embeddings using the company's internal AI infrastructure
    """
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.rdsec.trendmicro.com/prod/aiendpoint/v1/")
        self.chat_model_name = os.getenv("CHAT_MODEL", "gpt-4o")
        self.embedding_model_name = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
        
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. "
                "Please set your Trend Micro RDSec AI Endpoint API key."
            )
    
    def get_chat_model(self, 
                      model_name: Optional[str] = None,
                      temperature: float = 0.1,
                      max_tokens: int = 4096,
                      **kwargs) -> Any:
        """
        Get a configured chat model using Trend Micro's RDSec AI Endpoint
        
        Args:
            model_name: Model name (defaults to gpt-4o)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Additional model parameters
            
        Returns:
            Configured LangChain chat model
        """
        model = model_name or self.chat_model_name
        
        return init_chat_model(
            model,
            model_provider="openai",
            base_url=self.base_url,
            api_key=self.api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def get_embeddings_model(self, model_name: Optional[str] = None) -> OpenAIEmbeddings:
        """
        Get a configured embeddings model using Trend Micro's RDSec AI Endpoint
        
        Args:
            model_name: Embedding model name (defaults to text-embedding-3-large)
            
        Returns:
            Configured OpenAI embeddings model
        """
        model = model_name or self.embedding_model_name
        
        return OpenAIEmbeddings(
            model=model,
            openai_api_key=self.api_key,
            openai_api_base=self.base_url
        )
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current AI client configuration
        
        Returns:
            Dictionary with current configuration
        """
        return {
            "base_url": self.base_url,
            "chat_model": self.chat_model_name,
            "embedding_model": self.embedding_model_name,
            "api_key_configured": bool(self.api_key)
        }

# Global AI client instance
ai_client = AIClient()