"""
Helper functions
"""

import os
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

def generate_session_id() -> str:
    """
    Generates unique session ID
    
    Returns:
        Session ID in UUID format
    """
    return str(uuid.uuid4())

def format_timestamp(timestamp: datetime = None) -> str:
    """
    Formats timestamp
    
    Args:
        timestamp: Timestamp, uses current time if None
        
    Returns:
        Formatted time string
    """
    if timestamp is None:
        timestamp = datetime.now()
    
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncates text to specified length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def clean_filename(filename: str) -> str:
    """
    Cleans filename
    
    Args:
        filename: Filename to clean
        
    Returns:
        Cleaned filename
    """
    # Clean special characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    return filename.strip()

def ensure_directory_exists(directory_path: str):
    """
    Ensures directory exists, creates if it doesn't
    
    Args:
        directory_path: Directory path
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)

def calculate_similarity_percentage(score: float) -> str:
    """
    Converts similarity score to percentage format
    
    Args:
        score: Similarity score between 0-1
        
    Returns:
        String in percentage format
    """
    percentage = score * 100
    return f"{percentage:.1f}%"

def extract_file_extension(filename: str) -> str:
    """
    Extracts file extension
    
    Args:
        filename: Filename
        
    Returns:
        File extension (without dot)
    """
    return os.path.splitext(filename)[1].lower().lstrip('.')

def format_file_size(size_bytes: int) -> str:
    """
    Converts file size to readable format
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted file size
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names)-1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def validate_query(query: str) -> bool:
    """
    Validates query
    
    Args:
        query: Query to validate
        
    Returns:
        True if valid
    """
    if not query or not query.strip():
        return False
    
    if len(query.strip()) < 3:
        return False
    
    return True

def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extracts keywords from text
    
    Args:
        text: Text to analyze
        min_length: Minimum word length
        
    Returns:
        List of keywords
    """
    # Simple keyword extraction
    words = text.lower().split()
    
    # Stop words (Turkish and English)
    stop_words = {
        've', 'ile', 'bu', 'bir', 'için', 'den', 'dan', 'de', 'da',
        'ki', 'olan', 'olarak', 'olan', 'sonra', 'kadar', 'daha',
        'çok', 'az', 'gibi', 'ancak', 'fakat', 'ama', 'veya', 'ya',
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been'
    }
    
    keywords = []
    for word in words:
        # Clean
        word = word.strip('.,!?;:"()[]{}')
        
        # Check conditions
        if (len(word) >= min_length and 
            word.lower() not in stop_words and 
            word.isalpha()):
            keywords.append(word.lower())
    
    return list(set(keywords))  # Unique words 