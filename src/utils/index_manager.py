import os
import faiss
import json
import pickle
from typing import Dict, List, Any, Optional
from sentence_transformers import SentenceTransformer
from src.db.mongodb import MongoDB

class IndexManager:
    def __init__(self):
        """
        Initialize the index manager which handles FAISS indices for each user
        """
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.indices_dir = os.path.join(os.getcwd(), 'indices')
        os.makedirs(self.indices_dir, exist_ok=True)
        self.user_indices: Dict[str, Any] = {}
        self.user_docs: Dict[str, List[Dict[str, Any]]] = {}
        self.mongodb = MongoDB()
    
    def _get_index_path(self, user_id: str) -> str:
        """
        Get the path to a user's index file
        
        Args:
            user_id: User ID string
            
        Returns:
            Path to index file
        """
        return os.path.join(self.indices_dir, f"index_{user_id}.faiss")
    
    def _get_docs_path(self, user_id: str) -> str:
        """
        Get the path to a user's document metadata file
        
        Args:
            user_id: User ID string
            
        Returns:
            Path to document metadata file
        """
        return os.path.join(self.indices_dir, f"docs_{user_id}.pkl")
    
    def _format_inventory_docs(self, inventory_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Format inventory items into searchable documents
        
        Args:
            inventory_items: List of inventory items from MongoDB
            
        Returns:
            List of formatted documents
        """
        docs = []
        for item in inventory_items:
            item_name = item.get('item_name', 'Unknown Item')
            quantity = item.get('quantity', 0)
            price = item.get('price', 0)
            month = item.get('month', 'Unknown Month')
            
            # Create document with formatted text for better searching
            doc = {
                'text': f"Item: {item_name}, Quantity: {quantity}, Price: {price}, Month: {month}",
                'item_name': item_name,
                'quantity': quantity,
                'price': price,
                'month': month
            }
            docs.append(doc)
        return docs
    
    def get_or_create_index(self, user_id: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get or create a FAISS index for a specific user
        
        Args:
            user_id: User ID string
            force_refresh: Whether to force a refresh of the index
            
        Returns:
            Dictionary containing the index and document data
        """
        # If we already have this user's index and no refresh is needed, return it
        if user_id in self.user_indices and not force_refresh:
            return {
                'index': self.user_indices[user_id],
                'docs': self.user_docs[user_id]
            }
        
        index_path = self._get_index_path(user_id)
        docs_path = self._get_docs_path(user_id)
        
        # Check if index exists on disk and no refresh is needed
        if os.path.exists(index_path) and os.path.exists(docs_path) and not force_refresh:
            # Load index from disk
            index = faiss.read_index(index_path)
            with open(docs_path, 'rb') as f:
                docs = pickle.load(f)
            
            # Store in memory
            self.user_indices[user_id] = index
            self.user_docs[user_id] = docs
            
            return {
                'index': index,
                'docs': docs
            }
        
        # Create new index
        user_inventory = self.mongodb.get_user_inventory(user_id)
        user_bills = self.mongodb.get_user_bills(user_id)
        
        # Combine inventory and bills and format as documents
        all_items = user_inventory + user_bills
        docs = self._format_inventory_docs(all_items)
        
        if not docs:
            # If no documents, return empty results
            return {
                'index': None,
                'docs': []
            }
        
        # Create embeddings
        texts = [doc['text'] for doc in docs]
        embeddings = self.embedding_model.encode(texts)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        # Save to disk
        faiss.write_index(index, index_path)
        with open(docs_path, 'wb') as f:
            pickle.dump(docs, f)
        
        # Store in memory
        self.user_indices[user_id] = index
        self.user_docs[user_id] = docs
        
        return {
            'index': index,
            'docs': docs
        }
    
    def search(self, user_id: str, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Search a user's index for relevant documents
        
        Args:
            user_id: User ID string
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents
        """
        # Get or create index
        index_data = self.get_or_create_index(user_id)
        index = index_data['index']
        docs = index_data['docs']
        
        if index is None or not docs:
            return []
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search
        distances, indices = index.search(query_embedding, k=min(k, len(docs)))
        
        # Return matched documents
        results = [docs[idx] for idx in indices[0]]
        return results
    
    def refresh_index(self, user_id: str) -> Dict[str, Any]:
        """
        Force refresh a user's index
        
        Args:
            user_id: User ID string
            
        Returns:
            Dictionary with refresh status and document count
        """
        try:
            index_data = self.get_or_create_index(user_id, force_refresh=True)
            return {
                'status': 'success',
                'message': 'Index refreshed successfully',
                'document_count': len(index_data['docs'])
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to refresh index: {str(e)}',
                'document_count': 0
            }