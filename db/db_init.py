import sqlite3
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """
    Initialize the SQLite database if it doesn't exist.
    Creates the quotes table with specified columns if it doesn't exist.
    """
    db_path = "quotes.db"
    conn = None
    
    try:
        # Check if database exists
        if not os.path.exists(db_path):
            logger.info(f"Creating new database at {db_path}")
            
            # Connect to database (this will create it if it doesn't exist)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create quotes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS quotes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    book TEXT,
                    author TEXT,
                    entry_date DATETIME,
                    value INTEGER CHECK (value >= 1 AND value <= 10),
                    last_seen DATETIME
                )
            ''')
            
            conn.commit()
            logger.info("Database and table created successfully")
            
        else:
            logger.info(f"Database already exists at {db_path}")
            
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        if conn:
            conn.close()

