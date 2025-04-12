# Beaver RAG - Inventory Recipe Recommendation System

## Overview

Beaver RAG is a Retrieval-Augmented Generation (RAG) system for recipe recommendations based on user inventory data. It combines vector similarity search with large language models to provide personalized recipe suggestions that consider available ingredients and suggest missing ones.

## Features

- General-purpose RAG queries about inventory items
- Recipe recommendations based on available ingredients
- Structured recipe suggestions with detailed ingredient information
- Sri Lankan cuisine focus for lunch options
- User-specific inventory indexing for personalized results

## Technology Stack

- **Backend**: Flask web framework
- **Database**: MongoDB for user inventory/bills storage
- **Vector Search**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2 model)
- **LLM**: NVIDIA AI Endpoints (qwen2.5-7b-instruct model)
- **Workflow Orchestration**: LangGraph for RAG workflow
- **Deployment**: Docker containerization

## Project Structure

```
beaver_rag/
├── app.py                  # Main Flask application
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── src/
│   ├── config/            # Configuration settings
│   ├── db/                # Database connections
│   ├── langgraph/         # LangGraph workflow definitions
│   ├── models/            # Data models and prompts
│   ├── routes/            # API routes
│   └── utils/             # Utility functions
└── tests/                 # Unit tests
```

## API Endpoints

### 1. `/rag` (POST)

General-purpose RAG endpoint for inventory-related queries.

**Request:**
```json
{
  "query": "string (user question about inventory)",
  "userid": "string (MongoDB ObjectId)"
}
```

**Response:**
```json
{
  "answer": "string (natural language response)"
}
```

### 2. `/itemrag` (POST)

Specialized endpoint that returns recipe names as a JSON array.

**Request:**
```json
{
  "query": "string (recipe query)",
  "userid": "string (MongoDB ObjectId)"
}
```

**Response:**
```json
{
  "answer": ["Recipe1", "Recipe2", "Recipe3", ...]
}
```

### 3. `/new_item_recipe_suggestions_query` (POST)

Enhanced recipe suggestion endpoint with detailed ingredient information.

**Request:**
```json
{
  "query": "string (recipe query)",
  "userid": "string (MongoDB ObjectId)"
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "recipe_name": "Recipe Name",
      "additions": ["missing1", "missing2"],
      "base_ingredients": ["available1", "available2", "available3"]
    },
    ...
  ]
}
```

### 4. `/refresh` (POST)

Administrative endpoint to manually update user's vector index.

**Request:**
```json
{
  "userid": "string (MongoDB ObjectId)"
}
```

**Response:**
```json
{
  "status": "success|error",
  "message": "Description of result",
  "document_count": 123
}
```

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- MongoDB instance
- NVIDIA AI API key

### Environment Variables

Create a `.env` file with the following variables:

```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/inventory
MONGODB_DATABASE=inventory
NVIDIA_API_KEY=your_nvidia_api_key
PORT=7000
```

### Running with Docker

```bash
# Build and start the Docker container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

### Development Setup

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Testing

```bash
# Run tests
python -m unittest discover tests
```

## Core Components

### LangGraph RAG Workflow

The system uses LangGraph to orchestrate the RAG workflow:

1. **Retrieval**: Fetch relevant documents from the user's FAISS index
2. **Generation**: Use the LLM to generate responses based on the context
3. **Formatting**: Process the response into the appropriate output format

### Vector Search

The system maintains user-specific FAISS indices for efficient similarity search:

- Creates embeddings for inventory items using Sentence Transformers
- Searches for relevant items based on query similarity
- Automatically refreshes indices when needed

### Recipe Generation

The recipe suggestion system:

- Analyzes available ingredients in the user's inventory
- Suggests recipes that require minimal additional ingredients
- Focuses on Sri Lankan cuisine for lunch options
- Provides structured data about required and available ingredients

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.