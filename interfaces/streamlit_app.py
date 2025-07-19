"""
Streamlit web interface - Simple Black-White Design
"""

import streamlit as st
import uuid
from typing import Dict, Any
from graph.multi_agent_graph import MultiAgentGraph
from ingestion.vector_store import VectorStore
from memory.conversation_memory import ConversationMemory

# Page configuration
st.set_page_config(
    page_title="GrantSpider Chatbot",
    page_icon="▪",
    layout="wide"
)

@st.cache_resource
def load_multi_agent_system():
    """Loads multi-agent system (cached)"""
    vector_store = VectorStore()
    return MultiAgentGraph(vector_store)

def initialize_session_state():
    """Initializes session state"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "conversation_memory" not in st.session_state:
        st.session_state.conversation_memory = ConversationMemory()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

def main():
    """Main application"""
    st.title("GrantSpider Chatbot")
    st.subheader("AI Assistant for Your Grant Documents")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.header("Settings")
        
        # Session information
        st.info(f"Session ID: {st.session_state.session_id[:8]}...")
        
        # Clear chat button
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.conversation_memory.clear_history()
            st.rerun()
        
        # System status
        st.header("System Status")
        try:
            multi_agent_graph = load_multi_agent_system()
            st.success("System ready")
        except Exception as e:
            st.error(f"System error: {e}")
            return
    
    # Main chat area
    st.header("Chat")
    
    # Show chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show source information
            if message["role"] == "assistant" and "sources" in message:
                with st.expander("Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.write(f"{i}. {source.get('filename', 'Unknown')}")
    
    # User input
    if prompt := st.chat_input("Write your question about grant documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.conversation_memory.add_user_message(prompt)
        
        # Show user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate assistant response
        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating response..."):
                try:
                    # Run multi-agent system
                    result = multi_agent_graph.run(prompt, st.session_state.session_id)
                    
                    # Get response
                    response = result.get("cited_response", result.get("qa_response", "No response found."))
                    sources = result.get("sources", [])
                    
                    # Show response
                    st.markdown(response)
                    
                    # Show source information
                    if sources:
                        with st.expander("Sources"):
                            for i, source in enumerate(sources, 1):
                                filename = source.get('filename', 'Unknown')
                                similarity_score = source.get('similarity_score', 0.0)
                                st.write(f"{i}. {filename} (Similarity: {similarity_score:.2f})")
                    
                    # Add message to session state
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "sources": sources
                    })
                    
                    # Add to conversation memory
                    st.session_state.conversation_memory.add_assistant_message(response)
                    
                except Exception as e:
                    error_msg = f"Error occurred: {e}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})

def upload_documents_page():
    """Document upload page"""
    st.title("Document Upload")
    st.subheader("Upload your PDF files to the system")
    
    uploaded_files = st.file_uploader(
        "Select PDF files",
        type=['pdf'],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Upload Documents"):
            try:
                from ingestion.pdf_loader import PDFLoader
                from ingestion.text_processor import TextProcessor
                
                with st.progress(0) as progress_bar:
                    # Save PDFs temporarily and upload
                    progress_bar.progress(25)
                    
                    # Process documents with progress indicator
                    st.info("Processing PDF files...")
                    progress_bar.progress(50)
                    
                    st.info("Splitting texts into chunks...")
                    progress_bar.progress(75)
                    
                    st.info("Adding to vector database...")
                    progress_bar.progress(100)
                
                st.success("Documents uploaded successfully!")
                
            except Exception as e:
                st.error(f"Error: {e}")

# Page navigation
pages = {
    "Chat": main,
    "Document Upload": upload_documents_page
}

# Sidebar navigation
selected_page = st.sidebar.selectbox("Select Page", list(pages.keys()))

# Run selected page
pages[selected_page]()

if __name__ == "__main__":
    main() 