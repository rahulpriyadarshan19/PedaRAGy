# 📚 PedaRAGy - AI-Powered Learning Assistant

A sophisticated Retrieval-Augmented Generation (RAG) system that transforms your documents into an intelligent learning companion. PedaRAGy provides personalized explanations, interactive quizzes, and helpful hints based on your uploaded content.

## 🎯 Project Description

PedaRAGy is an advanced educational AI system that combines document processing, semantic search, and large language models to create an interactive learning experience. The system allows users to upload PDF documents, which are then processed, chunked, and embedded into a vector database for intelligent retrieval and response generation.

### Key Features

- **📁 Multi-Document Upload**: Process multiple PDF files simultaneously
- **🧠 Intelligent Chunking**: Advanced text segmentation for optimal context retrieval
- **🔍 Semantic Search**: Vector-based similarity search for relevant content
- **🤖 Multiple AI Modes**: 
  - 📖 **Explain**: Detailed explanations and insights
  - 🧠 **Quiz**: Interactive questions to test understanding
  - 💡 **Hint**: Guided hints without giving away answers
- **⚡ Semantic Caching**: Intelligent caching system for faster responses
- **🎨 Beautiful UI**: Modern Streamlit interface for seamless interaction
- **🔧 RESTful API**: Complete FastAPI backend for integration

## 🏗️ Architecture

### System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   File Upload   │  │  Q&A Interface  │  │ Cache Management│ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│           │                     │                     │         │
│           └─────────────────────┼─────────────────────┘         │
│                                 │                               │
│                    ┌─────────────────┐                         │
│                    │  Streamlit UI   │                         │
│                    └─────────────────┘                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                              │
│                    ┌─────────────────┐                         │
│                    │  FastAPI Server │                         │
│                    └─────────────────┘                         │
│           │           │           │           │                │
│           ▼           ▼           ▼           ▼                │
│  ┌─────────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐      │
│  │ add_data/   │ │ ask/    │ │ search/ │ │ cache/stats │      │
│  └─────────────┘ └─────────┘ └─────────┘ └─────────────┘      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Processing Layer                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │PDF Extractor│───▶│Text Chunking│───▶│Embedding    │        │
│  └─────────────┘    └─────────────┘    │Model        │        │
│                                         └─────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Storage Layer                            │
│                    ┌─────────────────┐                         │
│                    │Pinecone Vector  │                         │
│                    │Database         │                         │
│                    └─────────────────┘                         │
│           │                           │                        │
│           ▼                           ▼                        │
│  ┌─────────────┐              ┌─────────────┐                 │
│  │Document     │              │Cache Index  │                 │
│  │Index        │              │             │                 │
│  └─────────────┘              └─────────────┘                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         AI Layer                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │    LLM      │───▶│Prompt       │───▶│Response     │        │
│  │             │    │Templates    │    │Generation   │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Caching Layer                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│  │Semantic     │───▶│Similarity   │───▶│Response     │        │
│  │Cache        │    │Matching     │    │Retrieval    │        │
│  └─────────────┘    └─────────────┘    └─────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Document Upload**: User uploads PDFs → FastAPI processes → PDF extraction → Text chunking → Embedding generation → Vector storage
2. **Question Processing**: User asks question → Semantic cache check → Vector search → LLM processing → Response generation
3. **Caching**: Similar queries are cached for faster future responses

### System Components

1. **Frontend (Streamlit)**: User interface for document upload and interaction
2. **API Layer (FastAPI)**: RESTful endpoints for all operations
3. **Document Processing**: PDF extraction, chunking, and embedding generation
4. **Vector Database (Pinecone)**: Storage for document embeddings and semantic cache
5. **LLM Integration (Ollama)**: Local language model for response generation
6. **Semantic Caching**: Intelligent response caching based on query similarity

## 🚀 Installation Instructions

### Prerequisites

- Python 3.8+
- pip package manager
- Ollama installed and running (for LLM functionality)
- Pinecone account (for vector database)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd pedaragy
```

### Step 2: Create Virtual Environment

```bash
python -m venv pedaragy_env
source pedaragy_env/bin/activate  # On Windows: pedaragy_env\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install Streamlit dependencies
pip install -r requirements_streamlit.txt
```

### Step 4: Environment Configuration

Create a `.env` file in the project root:

```env
PINECONE_API_KEY=your_pinecone_api_key_here
```

### Step 5: Set Up Ollama

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull the required model:
```bash
ollama pull codegemma:7b
```
3. Start the Ollama service:
```bash
ollama serve
```

### Step 6: Start the Application

**Option A: Automated Startup (Recommended)**
```bash
python start_app.py
```

**Option B: Manual Startup**
```bash
# Terminal 1: Start FastAPI server
uvicorn app.main:app --reload

# Terminal 2: Start Streamlit app
streamlit run streamlit_app.py --server.port 8501
```

### Step 7: Access the Application

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **API Base**: http://localhost:8000

## 📊 Sample Input/Output

### 1. Document Upload

**Input (API Request):**
```json
POST /add_data/
{
  "file_paths": [
    "/path/to/machine_learning_textbook.pdf",
    "/path/to/statistics_guide.pdf"
  ]
}
```

**Output:**
```json
{
  "message": "Processed 2 files successfully",
  "processed_files": [
    "/path/to/machine_learning_textbook.pdf",
    "/path/to/statistics_guide.pdf"
  ],
  "total_chunks": 156,
  "failed_files": null
}
```

### 2. Question Asking - Explain Mode

**Input (API Request):**
```json
POST /ask/
{
  "prompt": "What is the difference between supervised and unsupervised learning?",
  "model": "codegemma:7b",
  "mode": "explain"
}
```

**Output:**
```json
{
  "answer": "Supervised learning and unsupervised learning are two fundamental approaches in machine learning:\n\n**Supervised Learning:**\n- Uses labeled training data where both input features and target outputs are known\n- The algorithm learns to map inputs to correct outputs\n- Examples: classification (predicting categories) and regression (predicting continuous values)\n- Common algorithms: Linear Regression, Decision Trees, Neural Networks\n\n**Unsupervised Learning:**\n- Works with unlabeled data where only input features are available\n- The algorithm finds hidden patterns or structures in the data\n- Examples: clustering (grouping similar data points) and dimensionality reduction\n- Common algorithms: K-Means, PCA, DBSCAN\n\nThe key difference is that supervised learning requires 'answers' (labels) to learn from, while unsupervised learning discovers patterns without any guidance.",
  "mode": "explain",
  "cached": false
}
```

### 3. Question Asking - Quiz Mode

**Input (API Request):**
```json
POST /ask/
{
  "prompt": "Explain neural networks",
  "model": "codegemma:7b",
  "mode": "quiz"
}
```

**Output:**
```json
{
  "answer": "Here are some questions to test your understanding of neural networks:\n\n**Basic Concepts:**\n1. What is the fundamental building block of a neural network?\n2. How does a perceptron differ from a multi-layer perceptron?\n3. What role do activation functions play in neural networks?\n\n**Architecture:**\n4. What is the difference between the input layer, hidden layers, and output layer?\n5. How do you determine the number of neurons in each layer?\n6. What is the purpose of bias terms in neural networks?\n\n**Learning Process:**\n7. Explain the forward propagation process.\n8. What is backpropagation and why is it important?\n9. How does gradient descent work in training neural networks?\n\n**Advanced Topics:**\n10. What are the advantages and disadvantages of deep neural networks?\n11. How do you prevent overfitting in neural networks?\n12. What is the vanishing gradient problem?\n\nTry answering these questions, and let me know if you need hints or explanations for any specific topic!",
  "mode": "quiz",
  "cached": false
}
```

### 4. Question Asking - Hint Mode

**Input (API Request):**
```json
POST /ask/
{
  "prompt": "How do I implement gradient descent?",
  "model": "codegemma:7b",
  "mode": "hint"
}
```

**Output:**
```json
{
  "answer": "Here are some hints to help you implement gradient descent:\n\n**Key Components to Consider:**\n- Start by understanding what gradient descent is trying to minimize (usually a cost function)\n- Think about the mathematical relationship between your parameters and the cost\n- Consider the learning rate - it's crucial for convergence\n\n**Implementation Steps:**\n- Calculate the gradient of your cost function with respect to each parameter\n- Update parameters in the opposite direction of the gradient\n- Repeat until convergence or maximum iterations\n\n**Important Considerations:**\n- The learning rate affects both speed and stability of convergence\n- You might want to implement different variants (batch, stochastic, mini-batch)\n- Consider adding momentum or adaptive learning rates for better performance\n\n**Debugging Tips:**\n- Plot your cost function over iterations to visualize convergence\n- Check if your gradients are being calculated correctly\n- Start with a simple example (like linear regression) before moving to complex models\n\nWould you like me to elaborate on any of these hints?",
  "mode": "hint",
  "cached": false
}
```

### 5. Cached Response

**Input (API Request):**
```json
POST /ask/
{
  "prompt": "What is supervised learning?",
  "model": "codegemma:7b",
  "mode": "explain"
}
```

**Output (Cached):**
```json
{
  "answer": "Supervised learning is a machine learning approach where algorithms learn from labeled training data...",
  "mode": "explain",
  "cached": true,
  "similarity_score": 0.97,
  "original_query": "What is the difference between supervised and unsupervised learning?"
}
```

### 6. Cache Statistics

**Input (API Request):**
```json
GET /cache/stats
```

**Output:**
```json
{
  "total_vectors": 45,
  "namespaces": {
    "default": 45
  },
  "dimension": 384,
  "metric": "cosine"
}
```

## 🛠️ API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message and available endpoints |
| `/add_data/` | POST | Upload and process multiple PDF files |
| `/ask/` | POST | Ask questions with different modes |
| `/search/` | POST | Search for similar content |
| `/cache/stats` | GET | Get cache statistics |
| `/cache/clear` | DELETE | Clear the semantic cache |

## 🔧 Configuration

### Environment Variables

- `PINECONE_API_KEY`: Your Pinecone API key for vector database access

### Model Configuration

- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions)
- **LLM Model**: codegemma:7b (via Ollama)
- **Similarity Threshold**: 95% for cache hits

## 📁 Project Structure

```
pedaragy/
├── app/
│   ├── embeddings/
│   │   └── embedding_model.py
│   ├── ingestion/
│   │   ├── pdf_extractor.py
│   │   └── docx_extractor.py
│   ├── llm/
│   │   ├── CallOllama/
│   │   ├── ollama_client.py
│   │   └── prompts.py
│   ├── preprocessing/
│   │   └── chunker.py
│   ├── vector_store/
│   │   ├── pinecone_client.py
│   │   ├── search.py
│   │   └── semantic_cache.py
│   └── main.py
├── streamlit_app.py
├── start_app.py
├── requirements.txt
├── requirements_streamlit.txt
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the [FastAPI documentation](http://localhost:8000/docs) when the server is running
- Review the [Streamlit documentation](https://docs.streamlit.io/)
- Open an issue in the repository

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the beautiful UI framework
- [FastAPI](https://fastapi.tiangolo.com/) for the robust API framework
- [Pinecone](https://www.pinecone.io/) for vector database services
- [Ollama](https://ollama.ai/) for local LLM hosting
- [sentence-transformers](https://www.sbert.net/) for embedding generation