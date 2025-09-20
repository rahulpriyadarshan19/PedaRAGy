# PedaRAGy - Streamlit UI

A beautiful and intuitive web interface for the PedaRAGy AI-powered learning assistant.

## Features

### 📁 Document Upload
- Upload multiple PDF files at once
- Automatic text extraction and chunking
- Real-time processing status
- Detailed upload results with success/failure information

### ❓ Interactive Q&A
- Three response modes:
  - **📖 Explain**: Detailed explanations and insights
  - **🧠 Quiz**: Test your understanding with questions
  - **💡 Hint**: Get helpful hints and guidance
- Semantic caching for faster responses
- Visual indicators for cached vs. fresh responses

### 📊 Cache Management
- View cache statistics and performance metrics
- Clear cache when needed
- Detailed information about how semantic caching works

## Installation

1. Install Streamlit dependencies:
```bash
pip install -r requirements_streamlit.txt
```

2. Make sure your FastAPI server is running:
```bash
uvicorn app.main:app --reload
```

## Running the Application

### Option 1: Manual Start
1. Start the FastAPI server (in one terminal):
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

2. Start the Streamlit app (in another terminal):
```bash
streamlit run streamlit_app.py --server.port 8501
```

### Option 2: Automated Start
Use the startup script to run both services:
```bash
python start_app.py
```

## Accessing the Application

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **API Base**: http://localhost:8000

## Usage Guide

### 1. Upload Documents
1. Navigate to the "📁 Upload Documents" page
2. Select one or more PDF files
3. Click "🚀 Upload and Process Files"
4. Wait for processing to complete
5. Review the results and any failed files

### 2. Ask Questions
1. Go to the "❓ Ask Questions" page
2. Select your preferred response mode:
   - **Explain**: For detailed explanations
   - **Quiz**: For testing your knowledge
   - **Hint**: For guided learning
3. Type your question in the text area
4. Click "🔍 Ask Question"
5. Review the AI response and any cache indicators

### 3. Manage Cache
1. Visit the "📊 Cache Management" page
2. Click "🔄 Refresh Cache Statistics" to see current cache status
3. Use "🗑️ Clear All Cache" to reset the cache when needed

## Features Explained

### Semantic Caching
- The system automatically caches questions and answers
- Similar questions (95%+ similarity) get instant cached responses
- Cache indicators show when responses are retrieved from cache
- Improves performance and reduces API costs

### Response Modes
- **Explain Mode**: Provides comprehensive explanations with context from your documents
- **Quiz Mode**: Generates questions to test your understanding
- **Hint Mode**: Offers helpful hints and guidance without giving away answers

### File Processing
- Supports multiple PDF uploads simultaneously
- Automatic text extraction and intelligent chunking
- Robust error handling for problematic files
- Detailed processing reports

## Troubleshooting

### API Connection Issues
- Ensure the FastAPI server is running on port 8000
- Check that no firewall is blocking the connection
- Verify the API_BASE_URL in streamlit_app.py matches your setup

### File Upload Issues
- Ensure PDF files are not corrupted or password-protected
- Check file size limits (very large files may timeout)
- Review error messages in the upload results

### Performance Issues
- Use the cache management features to monitor performance
- Clear cache if responses seem outdated
- Consider reducing the number of files uploaded at once

## Customization

### Styling
The app uses custom CSS for a modern look. You can modify the styling in the `st.markdown()` section at the top of `streamlit_app.py`.

### API Configuration
Change the `API_BASE_URL` variable in `streamlit_app.py` if your FastAPI server runs on a different host/port.

### Timeouts
Adjust timeout values in the request functions if you need longer processing times for large files.

## Support

For issues or questions:
1. Check the FastAPI server logs for backend errors
2. Review the Streamlit app logs for frontend issues
3. Ensure all dependencies are properly installed
4. Verify your environment variables are set correctly
