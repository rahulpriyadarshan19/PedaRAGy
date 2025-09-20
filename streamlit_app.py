import streamlit as st
import requests
import os
from typing import List, Dict, Any

# Configure Streamlit page
st.set_page_config(
    page_title="PedaRAGy - AI-Powered Learning Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    
    .error-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        margin: 1rem 0;
    }
    
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    
    .cached-response {
        border-left: 4px solid #28a745;
        padding-left: 1rem;
        background-color: #f8f9fa;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

def check_api_connection() -> bool:
    """Check if the API is running and accessible."""
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def upload_files(files: List[Any]) -> Dict[str, Any]:
    """Upload multiple files to the API."""
    file_paths = []
    
    # Save uploaded files temporarily
    for file in files:
        if file is not None:
            # Create uploads directory if it doesn't exist
            os.makedirs("uploads", exist_ok=True)
            
            # Save file
            file_path = f"uploads/{file.name}"
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())
            file_paths.append(os.path.abspath(file_path))
    
    if not file_paths:
        return {"error": "No files selected"}
    
    # Send request to API
    try:
        response = requests.post(
            f"{API_BASE_URL}/add_data/",
            json={"file_paths": file_paths},
            timeout=300  # 5 minutes timeout for large files
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code} - {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection Error: {str(e)}"}

def ask_question(prompt: str, model: str, mode: str) -> Dict[str, Any]:
    """Send a question to the API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/ask/",
            json={
                "prompt": prompt,
                "model": model,
                "mode": mode
            },
            timeout=120  # 2 minutes timeout
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code} - {response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection Error: {str(e)}"}

def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/cache/stats", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection Error: {str(e)}"}

def clear_cache() -> Dict[str, Any]:
    """Clear the semantic cache."""
    try:
        response = requests.delete(f"{API_BASE_URL}/cache/clear", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection Error: {str(e)}"}

def main():
    # Main header
    st.markdown('<h1 class="main-header">📚 PedaRAGy</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Learning Assistant with Semantic Caching</p>', unsafe_allow_html=True)
    
    # Check API connection
    if not check_api_connection():
        st.error("❌ Cannot connect to the API. Please make sure the FastAPI server is running on http://localhost:8000")
        st.stop()
    
    # Sidebar for navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.selectbox("Choose a page", ["📁 Upload Documents", "❓ Ask Questions", "📊 Cache Management"])
    
    if page == "📁 Upload Documents":
        upload_documents_page()
    elif page == "❓ Ask Questions":
        ask_questions_page()
    elif page == "📊 Cache Management":
        cache_management_page()

def upload_documents_page():
    st.markdown('<h2 class="sub-header">📁 Upload Documents</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    Upload your PDF documents to build a knowledge base. The system will:
    - Extract text from your PDFs
    - Chunk the content intelligently
    - Generate embeddings for semantic search
    - Store everything in the vector database
    """)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        help="Select one or more PDF files to upload"
    )
    
    if uploaded_files:
        st.info(f"📄 {len(uploaded_files)} file(s) selected for upload")
        
        # Show file details
        with st.expander("📋 File Details"):
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"{i}. **{file.name}** ({file.size:,} bytes)")
        
        # Upload button
        if st.button("🚀 Upload and Process Files", type="primary"):
            with st.spinner("Processing files... This may take a few minutes."):
                result = upload_files(uploaded_files)
            
            if "error" in result:
                st.error(f"❌ Upload failed: {result['error']}")
            else:
                st.success("✅ Files uploaded and processed successfully!")
                
                # Display results
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Files Processed", result.get("processed_files", []).__len__())
                with col2:
                    st.metric("Total Chunks", result.get("total_chunks", 0))
                with col3:
                    failed_count = len(result.get("failed_files", []))
                    st.metric("Failed Files", failed_count, delta=None if failed_count == 0 else f"-{failed_count}")
                
                # Show processed files
                if result.get("processed_files"):
                    st.markdown("**✅ Successfully processed files:**")
                    for file in result["processed_files"]:
                        st.write(f"• {os.path.basename(file)}")
                
                # Show failed files if any
                if result.get("failed_files"):
                    st.markdown("**❌ Failed files:**")
                    for failed in result["failed_files"]:
                        st.write(f"• {os.path.basename(failed['file'])}: {failed['error']}")

def ask_questions_page():
    st.markdown('<h2 class="sub-header">❓ Ask Questions</h2>', unsafe_allow_html=True)
    
    # Mode selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        mode = st.selectbox(
            "🎯 Select Response Mode",
            ["explain", "quiz", "hint"],
            format_func=lambda x: {
                "explain": "📖 Explain - Detailed explanations and insights",
                "quiz": "🧠 Quiz - Test your understanding with questions",
                "hint": "💡 Hint - Get helpful hints and guidance"
            }[x],
            help="Choose how you want the AI to respond to your questions"
        )
    
    with col2:
        model = st.selectbox(
            "🤖 AI Model",
            ["codegemma:7b"],
            help="Select the AI model to use"
        )
    
    # Question input
    prompt = st.text_area(
        "💭 Your Question",
        placeholder="Ask anything about your uploaded documents...",
        height=100,
        help="Type your question here. The AI will search through your uploaded documents to provide relevant answers."
    )
    
    # Ask button
    if st.button("🔍 Ask Question", type="primary", disabled=not prompt.strip()):
        if not prompt.strip():
            st.warning("Please enter a question first.")
        else:
            with st.spinner("Thinking... This may take a moment."):
                result = ask_question(prompt, model, mode)
            
            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
            else:
                # Display response
                st.markdown("### 🤖 AI Response")
                
                # Check if response was cached
                if result.get("cached", False):
                    st.markdown('<div class="cached-response">', unsafe_allow_html=True)
                    st.success("⚡ This response was retrieved from cache for faster delivery!")
                    if result.get("similarity_score"):
                        st.info(f"📊 Similarity to original query: {result['similarity_score']:.2%}")
                    if result.get("original_query"):
                        st.info(f"🔍 Original cached query: \"{result['original_query']}\"")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Display the actual response
                st.markdown(result.get("answer", "No response received"))
                
                # Show mode used
                mode_emoji = {"explain": "📖", "quiz": "🧠", "hint": "💡"}
                st.caption(f"Response mode: {mode_emoji.get(mode, '❓')} {mode.title()}")

def cache_management_page():
    st.markdown('<h2 class="sub-header">📊 Cache Management</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    The semantic cache stores previous questions and answers to provide faster responses 
    for similar queries. This helps improve performance and reduces API calls.
    """)
    
    # Get cache stats
    if st.button("🔄 Refresh Cache Statistics"):
        with st.spinner("Loading cache statistics..."):
            stats = get_cache_stats()
        
        if "error" in stats:
            st.error(f"❌ Error: {stats['error']}")
        else:
            st.success("✅ Cache statistics loaded!")
            
            # Display stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Vectors", stats.get("total_vectors", 0))
            
            with col2:
                st.metric("Dimension", stats.get("dimension", 0))
            
            with col3:
                metric = stats.get("metric", "Unknown")
                st.metric("Similarity Metric", metric)
            
            # Show namespace details
            if stats.get("namespaces"):
                st.markdown("### 📁 Namespace Details")
                for namespace, count in stats["namespaces"].items():
                    st.write(f"• **{namespace}**: {count} vectors")
    
    # Clear cache section
    st.markdown("### 🗑️ Clear Cache")
    st.warning("⚠️ Clearing the cache will remove all stored questions and answers. This action cannot be undone.")
    
    if st.button("🗑️ Clear All Cache", type="secondary"):
        if st.session_state.get("confirm_clear", False):
            with st.spinner("Clearing cache..."):
                result = clear_cache()
            
            if "error" in result:
                st.error(f"❌ Error: {result['error']}")
            else:
                st.success("✅ Cache cleared successfully!")
                st.session_state.confirm_clear = False
        else:
            st.session_state.confirm_clear = True
            st.warning("Click the button again to confirm cache clearing.")
    
    # Cache information
    with st.expander("ℹ️ About Semantic Caching"):
        st.markdown("""
        **How it works:**
        1. When you ask a question, the system first checks if a similar question was asked before
        2. If a similar question is found (above 95% similarity), it returns the cached response
        3. If no similar question is found, it processes your question normally and caches the result
        
        **Benefits:**
        - ⚡ Faster response times for similar questions
        - 💰 Reduced API costs
        - 🔄 Consistent responses for similar queries
        
        **Cache Settings:**
        - Similarity threshold: 95%
        - Vector dimension: 384
        - Similarity metric: Cosine similarity
        """)

if __name__ == "__main__":
    main()
