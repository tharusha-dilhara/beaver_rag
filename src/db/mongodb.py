import os
from pymongo import MongoClient
from typing import Dict, List, Any

class MongoDB:
    def __init__(self):
        """
        Initialize MongoDB connection
        """
        self.mongodb_uri = os.environ.get("MONGODB_URI")
        self.db_name = os.environ.get("MONGODB_DATABASE", "inventory")
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client[self.db_name]
    
    def get_user_inventory(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve inventory items for a specific user
        
        Args:
            user_id: MongoDB ObjectId as string for the user
            
        Returns:
            List of inventory items
        """
        try:
            inventory_collection = self.db["inventories"]
            user_inventory = inventory_collection.find({"user_id": user_id})
            return list(user_inventory)
        except Exception as e:
            print(f"Error retrieving user inventory: {e}")
            return []
    
    def get_user_bills(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve bill items for a specific user
        
        Args:
            user_id: MongoDB ObjectId as string for the user
            
        Returns:
            List of bill items
        """
        try:
            bills_collection = self.db["bills"]
            user_bills = bills_collection.find({"user_id": user_id})
            return list(user_bills)
        except Exception as e:
            print(f"Error retrieving user bills: {e}")
            return []