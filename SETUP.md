# Setup, Testing and Deployment Guide

## Local Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd beaver_rag
```

### 2. Create and activate virtual environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the project root:
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/inventory
MONGODB_DATABASE=inventory
NVIDIA_API_KEY=your_nvidia_api_key
PORT=7000
```

### 5. Run the application
```bash
python app.py
```
The API will be available at http://localhost:7000

## Testing

### Running unit tests
```bash
# Run all tests
python -m unittest discover tests

# Run a specific test file
python -m unittest tests.test_rag_api
```

### Manual API testing with curl
```bash
# Test /rag endpoint
curl -X POST http://localhost:7000/rag \
  -H "Content-Type: application/json" \
  -d '{"query": "What items do I have?", "userid": "user123"}'

# Test /itemrag endpoint
curl -X POST http://localhost:7000/itemrag \
  -H "Content-Type: application/json" \
  -d '{"query": "What lunch recipes can I make?", "userid": "user123"}'

# Test /new_item_recipe_suggestions_query endpoint
curl -X POST http://localhost:7000/new_item_recipe_suggestions_query \
  -H "Content-Type: application/json" \
  -d '{"query": "What lunch recipes can I make?", "userid": "user123"}'

# Test /refresh endpoint
curl -X POST http://localhost:7000/refresh \
  -H "Content-Type: application/json" \
  -d '{"userid": "user123"}'
```

## Docker Deployment

### Local Docker deployment

1. Build and start the Docker container:
```bash
docker-compose up -d
```

2. View container logs:
```bash
docker-compose logs -f
```

3. Stop the container:
```bash
docker-compose down
```

### Cloud Deployment Options

#### AWS Elastic Container Service (ECS)

1. Push Docker image to Amazon ECR:
```bash
# Authenticate with ECR
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

# Create repository
aws ecr create-repository --repository-name beaver-rag --region <region>

# Tag image
docker tag beaver-rag:latest <account-id>.dkr.ecr.<region>.amazonaws.com/beaver-rag:latest

# Push image
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/beaver-rag:latest
```

2. Create an ECS cluster, task definition, and service through the AWS console or CLI.

#### Google Cloud Run

1. Push Docker image to Google Container Registry:
```bash
# Configure Docker to use gcloud credentials
gcloud auth configure-docker

# Build and tag the image
docker build -t gcr.io/<project-id>/beaver-rag .

# Push the image
docker push gcr.io/<project-id>/beaver-rag
```

2. Deploy the image to Cloud Run:
```bash
gcloud run deploy beaver-rag \
  --image gcr.io/<project-id>/beaver-rag \
  --platform managed \
  --region <region> \
  --allow-unauthenticated
```

#### Azure Container Instances

1. Push Docker image to Azure Container Registry:
```bash
# Log in to Azure
az login

# Create a resource group
az group create --name myResourceGroup --location eastus

# Create a container registry
az acr create --resource-group myResourceGroup --name <registry-name> --sku Basic

# Log in to the registry
az acr login --name <registry-name>

# Tag the image
docker tag beaver-rag:latest <registry-name>.azurecr.io/beaver-rag:latest

# Push the image
docker push <registry-name>.azurecr.io/beaver-rag:latest
```

2. Deploy to Azure Container Instances:
```bash
az container create \
  --resource-group myResourceGroup \
  --name beaver-rag \
  --image <registry-name>.azurecr.io/beaver-rag:latest \
  --dns-name-label beaver-rag \
  --ports 7000 \
  --environment-variables \
    MONGODB_URI='<your-mongodb-uri>' \
    MONGODB_DATABASE='inventory' \
    NVIDIA_API_KEY='<your-nvidia-api-key>'
```

## Performance Monitoring

### Adding Prometheus Metrics

1. Install Prometheus client:
```bash
pip install prometheus-client
```

2. Add to requirements.txt:
```
prometheus-client==0.16.0
```

3. Implement metrics in app.py:
```python
from prometheus_client import Counter, Histogram, start_http_server

# Create metrics
REQUEST_COUNT = Counter('rag_request_count', 'Total RAG API requests', ['endpoint'])
REQUEST_LATENCY = Histogram('rag_request_latency_seconds', 'Request latency in seconds', ['endpoint'])

# Start Prometheus metrics server
start_http_server(8000)
```

4. Access metrics at: http://localhost:8000

## CI/CD Setup

### GitHub Actions Example (.github/workflows/ci.yml)
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        python -m unittest discover tests

  deploy:
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Login to DockerHub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    - name: Build and push
      uses: docker/build-push-action@v2
      with:
        push: true
        tags: yourusername/beaver-rag:latest
```