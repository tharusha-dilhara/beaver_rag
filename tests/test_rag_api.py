import unittest
import json
from unittest.mock import patch, MagicMock
from app import app

class TestRAGAPI(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    @patch('src.routes.rag_routes.invoke_rag')
    def test_rag_endpoint(self, mock_invoke_rag):
        # Mock response
        mock_invoke_rag.return_value = {"response": "Test response"}
        
        # Test request
        response = self.app.post('/rag',
                               data=json.dumps({"query": "What items do I have?", "userid": "user123"}),
                               content_type='application/json')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["answer"], "Test response")
        
        # Verify mock was called with correct parameters
        mock_invoke_rag.assert_called_once_with(
            query="What items do I have?",
            user_id="user123",
            output_type="text",
            index_manager=unittest.mock.ANY,
            llm_client=unittest.mock.ANY
        )
    
    @patch('src.routes.rag_routes.invoke_rag')
    def test_itemrag_endpoint(self, mock_invoke_rag):
        # Mock response
        mock_invoke_rag.return_value = {"recipe_list": ["Recipe 1", "Recipe 2"]}
        
        # Test request
        response = self.app.post('/itemrag',
                               data=json.dumps({"query": "lunch recipes", "userid": "user123"}),
                               content_type='application/json')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["answer"], ["Recipe 1", "Recipe 2"])
        
        # Verify mock was called with correct parameters
        mock_invoke_rag.assert_called_once_with(
            query="lunch recipes",
            user_id="user123",
            output_type="recipe_list",
            index_manager=unittest.mock.ANY,
            llm_client=unittest.mock.ANY
        )
    
    @patch('src.routes.rag_routes.invoke_rag')
    def test_structured_recipe_endpoint(self, mock_invoke_rag):
        # Mock response
        mock_result = {
            "structured_suggestions": [
                {
                    "recipe_name": "Recipe 1",
                    "additions": ["item1", "item2"],
                    "base_ingredients": ["ing1", "ing2"]
                }
            ]
        }
        mock_invoke_rag.return_value = mock_result
        
        # Test request
        response = self.app.post('/new_item_recipe_suggestions_query',
                               data=json.dumps({"query": "detailed recipes", "userid": "user123"}),
                               content_type='application/json')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["suggestions"], mock_result["structured_suggestions"])
        
        # Verify mock was called with correct parameters
        mock_invoke_rag.assert_called_once_with(
            query="detailed recipes",
            user_id="user123",
            output_type="structured",
            index_manager=unittest.mock.ANY,
            llm_client=unittest.mock.ANY
        )
    
    @patch('src.routes.rag_routes.index_manager')
    def test_refresh_endpoint(self, mock_index_manager):
        # Mock response
        mock_result = {
            "status": "success",
            "message": "Index refreshed successfully",
            "document_count": 10
        }
        mock_index_manager.refresh_index.return_value = mock_result
        
        # Test request
        response = self.app.post('/refresh',
                               data=json.dumps({"userid": "user123"}),
                               content_type='application/json')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data, mock_result)
        
        # Verify mock was called with correct parameters
        mock_index_manager.refresh_index.assert_called_once_with("user123")

if __name__ == '__main__':
    unittest.main()