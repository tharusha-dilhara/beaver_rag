from flask import Blueprint, request, jsonify
from src.utils.index_manager import IndexManager
from src.utils.llm_client import LLMClient
from src.langgraph.rag_graph import invoke_rag
from typing import Dict, Any, List

# Initialize resources
index_manager = IndexManager()
llm_client = LLMClient()

# Create blueprint
rag_bp = Blueprint('rag', __name__)

@rag_bp.route('/rag', methods=['POST'])
def rag_endpoint():
    """
    General-purpose RAG endpoint for inventory-related queries.
    """
    try:
        # Parse request
        data = request.json
        if not data or 'query' not in data or 'userid' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
            
        query = data['query']
        user_id = data['userid']
        
        # Invoke RAG workflow
        result = invoke_rag(
            query=query,
            user_id=user_id,
            output_type="text",
            index_manager=index_manager,
            llm_client=llm_client
        )
        
        # Return response
        return jsonify({"answer": result["response"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@rag_bp.route('/itemrag', methods=['POST'])
def item_rag_endpoint():
    """
    Specialized endpoint that returns recipe names as a JSON array.
    """
    try:
        # Parse request
        data = request.json
        if not data or 'query' not in data or 'userid' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
            
        query = data['query']
        user_id = data['userid']
        
        # Invoke RAG workflow
        result = invoke_rag(
            query=query,
            user_id=user_id,
            output_type="recipe_list",
            index_manager=index_manager,
            llm_client=llm_client
        )
        
        # Return recipe list
        return jsonify({"answer": result["recipe_list"]})
    except Exception as e:
        return jsonify({"answer": [f"Error generating recipes: {str(e)}"]}), 200

@rag_bp.route('/new_item_recipe_suggestions_query', methods=['POST'])
def structured_recipe_endpoint():
    """
    Enhanced recipe suggestion endpoint with detailed ingredient information.
    """
    try:
        # Parse request
        data = request.json
        if not data or 'query' not in data or 'userid' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
            
        query = data['query']
        user_id = data['userid']
        
        # Invoke RAG workflow
        result = invoke_rag(
            query=query,
            user_id=user_id,
            output_type="structured",
            index_manager=index_manager,
            llm_client=llm_client
        )
        
        # Return structured suggestions
        return jsonify({"suggestions": result["structured_suggestions"]})
    except Exception as e:
        return jsonify({"suggestions": [{"error": str(e)}]}), 200

@rag_bp.route('/refresh', methods=['POST'])
def refresh_index_endpoint():
    """
    Administrative endpoint to manually update user's vector index.
    """
    try:
        # Parse request
        data = request.json
        if not data or 'userid' not in data:
            return jsonify({"error": "Missing userid parameter"}), 400
            
        user_id = data['userid']
        
        # Refresh index
        result = index_manager.refresh_index(user_id)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "document_count": 0
        }), 500