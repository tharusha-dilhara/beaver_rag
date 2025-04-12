import os
from typing import Dict, Any

class Config:
    """
    Configuration class for the application
    """
    
    @staticmethod
    def get_llm_config() -> Dict[str, Any]:
        """
        Get LLM configuration
        
        Returns:
            Dictionary with LLM configuration parameters
        """
        return {
            "api_key": os.environ.get("NVIDIA_API_KEY"),
            "model": "qwen2.5-7b-instruct"
        }
    
    @staticmethod
    def get_embedding_config() -> Dict[str, str]:
        """
        Get embedding model configuration
        
        Returns:
            Dictionary with embedding model parameters
        """
        return {
            "model_name": "all-MiniLM-L6-v2"
        }