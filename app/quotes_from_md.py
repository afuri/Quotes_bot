import logging
from typing import List
from app.book import Book_quotes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_md_to_quotes(file_path: str) -> Book_quotes:
    """
    Parses a markdown file and returns a Book_quotes instance.
    
    Args:
        file_path (str): Path to the markdown file
        
    Returns:
        Book_quotes: Instance containing book metadata and quotes
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Split content by "---"
        sections = content.split('---')

        if len(sections) < 3:
            raise ValueError("Invalid markdown format: expected at least 3 sections")
 
        # Parse metadata from first section
        metadata = sections[1].strip()
        title = None
        author = None
        
        for line in metadata.split('\n'):
            if line.startswith('Название:'):
                title = line.replace('Название:', '').strip()
            elif line.startswith('Автор:'):
                author = line.replace('Автор:', '').strip()
                
        if not title or not author:
            raise ValueError("Missing required metadata: title or author")
            
        # Parse quotes from third section
        quotes = []
        for block in sections[3:]:
            block = block.strip()
            if block:  # Skip empty blocks
                quotes.append(block)
                
        if not quotes:
            raise ValueError("No quotes found in the file")
            
        logger.info(f"Successfully parsed {len(quotes)} quotes from '{title}'")
        
        return Book_quotes(
            book=title,
            author=author,
            content=quotes,
            value=5  # Default value
        )
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error parsing markdown file: {e}")
        raise

