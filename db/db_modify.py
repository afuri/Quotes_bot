import sqlite3
import logging
from datetime import datetime
from typing import Union, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def modify_cell(id: int, column: str, new_value: Any) -> None:
    """
    Modifies a specific cell in the quotes database.
    
    Args:
        id (int): The ID of the row to modify
        column (str): The name of the column to modify
        new_value (Any): The new value to set. Type must match the column type:
            - content, book, author: str
            - entry_date, last_seen: datetime
            - value: int (1-10)
        
    Raises:
        ValueError: If the column name is invalid or value type doesn't match column type
        sqlite3.Error: If there's a database error
    """
    # Dictionary mapping columns to their expected types and validation rules
    column_types = {
        'content': {'type': str, 'nullable': False},
        'book': {'type': str, 'nullable': True},
        'author': {'type': str, 'nullable': True},
        'entry_date': {'type': datetime, 'nullable': True},
        'value': {'type': int, 'nullable': True, 'min': 1, 'max': 10},
        'last_seen': {'type': datetime, 'nullable': True}
    }
    
    # Validate column name
    if column not in column_types:
        raise ValueError(f"Invalid column name. Must be one of: {', '.join(column_types.keys())}")
    
    # Validate value type and constraints
    if new_value is None:
        if not column_types[column]['nullable']:
            raise ValueError(f"Column {column} cannot be NULL")
    else:
        if not isinstance(new_value, column_types[column]['type']):
            raise ValueError(f"Column {column} must be of type {column_types[column]['type'].__name__}")
        
        # Additional validation for value column
        if column == 'value' and not (column_types[column]['min'] <= new_value <= column_types[column]['max']):
            raise ValueError(f"Value must be between {column_types[column]['min']} and {column_types[column]['max']}")
    
    db_path = "quotes.db"
    conn = None
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update the specified cell
        cursor.execute(f'''
            UPDATE quotes 
            SET {column} = ? 
            WHERE id = ?
        ''', (new_value, id))
        
        # Check if any row was affected
        if cursor.rowcount == 0:
            logger.warning(f"No row found with id {id}")
        else:
            conn.commit()
            logger.info(f"Successfully updated {column} for id {id}")
            
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
    finally:
        if conn:
            conn.close()


