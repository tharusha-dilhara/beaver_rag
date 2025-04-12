from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from flask_cors import CORS
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from src.routes.rag_routes import rag_bp
from src.utils.index_manager import IndexManager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize IndexManager
index_manager = IndexManager()

# Register blueprints
app.register_blueprint(rag_bp)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7000))
    app.run(host="0.0.0.0", port=port, debug=False)