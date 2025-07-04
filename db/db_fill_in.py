import sqlite3
import logging
from datetime import datetime
from app.book import Book_quotes
import os
from db.db_init import init_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def db_fill_in(book_quotes: Book_quotes) -> None:
    """
    Fills the database with quotes from a Book_quotes instance.
    
    Args:
        book_quotes (Book_quotes): An instance of Book_quotes containing quotes to be added
    """
    db_path = "quotes.db"
    if not os.path.exists(db_path):
        init_database()
    conn = None
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get current date for entry_date and last_seen
        current_date = datetime.now()
        
        # Insert each quote from the content list
        for quote in book_quotes.content:
            cursor.execute('''
                INSERT INTO quotes (content, book, author, entry_date, value, last_seen)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (quote, book_quotes.book, book_quotes.author, current_date, book_quotes.value, current_date))
            
        conn.commit()
        logger.info(f"Successfully added {len(book_quotes.content)} quotes from '{book_quotes.book}' to database")
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        if conn:
            conn.close()

