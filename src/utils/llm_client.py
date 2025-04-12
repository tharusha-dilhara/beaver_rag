import os
from typing import Dict, Any, List, Optional
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain.schema import HumanMessage, SystemMessage
import json
import re

class LLMClient:
    def __init__(self):
        """
        Initialize LLM client for NVIDIA AI Endpoints
        """
        self.api_key = os.environ.get("NVIDIA_API_KEY")
        self.llm = ChatNVIDIA(
            api_key=self.api_key,
            model="qwen2.5-7b-instruct"
        )
    
    def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generate a response from the LLM
        
        Args:
            system_prompt: System prompt to set context
            user_prompt: User query with context
            
        Returns:
            LLM response as string
        """
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
    
    def parse_recipe_list(self, response: str) -> List[str]:
        """
        Parse LLM response into a list of recipe names
        
        Args:
            response: LLM response string that should contain recipe names
            
        Returns:
            List of recipe names
        """
        # Try to parse as JSON first
        try:
            # Check if response contains a JSON array
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                recipes = json.loads(json_str)
                if isinstance(recipes, list):
                    return recipes
        except json.JSONDecodeError:
            pass
        
        # Fallback to line-by-line parsing
        recipes = []
        for line in response.split('\n'):
            # Remove numbering, bullets, etc.
            cleaned_line = re.sub(r'^\s*\d+\.\s*|^\s*-\s*|^\s*\*\s*', '', line).strip()
            if cleaned_line:
                recipes.append(cleaned_line)
        
        return recipes
    
    def parse_structured_suggestions(self, response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response into structured recipe suggestions
        
        Args:
            response: LLM response string that should contain structured recipe data
            
        Returns:
            List of recipe suggestion objects
        """
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\[\s*{.*}\s*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                suggestions = json.loads(json_str)
                if isinstance(suggestions, list):
                    return suggestions
            
            # If no valid JSON array found, try to parse as a JSON object
            json_obj_match = re.search(r'{\s*"suggestions"\s*:\s*\[.*\]\s*}', response, re.DOTALL)
            if json_obj_match:
                json_str = json_obj_match.group(0)
                parsed = json.loads(json_str)
                if isinstance(parsed, dict) and 'suggestions' in parsed:
                    return parsed['suggestions']
        except json.JSONDecodeError:
            # If JSON parsing fails, return error as structured response
            return [{'error': 'Failed to parse suggestions from LLM response'}]
        
        # If all parsing attempts fail
        return [{'error': 'Failed to extract structured recipe suggestions from response'}]