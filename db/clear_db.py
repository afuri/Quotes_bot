import sqlite3
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_database():
    """
    Deletes all entries from the quotes table in the database.
    The table structure remains intact, only the data is removed.
    """
    db_path = "quotes.db"
    conn = None
    
    try:
        # Check if database exists
        if not os.path.exists(db_path):
            logger.error(f"Database not found at {db_path}")
            return
            
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Delete all entries from quotes table
        cursor.execute("DELETE FROM quotes")
        
        # Commit the changes
        conn.commit()
        
        # Get the number of deleted rows
        deleted_rows = cursor.rowcount
        logger.info(f"Successfully deleted {deleted_rows} entries from quotes table")
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        if conn:
            conn.close()
