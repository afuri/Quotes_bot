import sqlite3
import json
from datetime import datetime, timedelta
from db.db_modify import modify_cell
import random

def get_random_quote():
    """
    Gets a random quote from the database where last_seen is earlier than current time.
    Uses efficient random selection for large datasets.
    Returns the quote data as JSON.
    """
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect('quotes.db')
        cursor = conn.cursor()
        
        # Get current time
        current_time = datetime.now()
        
        # First, get the count of available quotes
        cursor.execute("""
            SELECT COUNT(*) 
            FROM quotes 
            WHERE last_seen < ?
        """, (current_time,))
        
        count = cursor.fetchone()[0]
        
        if count == 0:
            return json.dumps({'error': 'No quotes available'})
            
        # Get a random offset
        random_offset = random.randint(0, count - 1)
        
        # Query to get a quote at the random offset
        cursor.execute("""
            SELECT id, content, book, author, entry_date, value, last_seen 
            FROM quotes 
            WHERE last_seen < ? 
            LIMIT 1 OFFSET ?
        """, (current_time, random_offset))
        
        # Get the result
        result = cursor.fetchone()
        
        if result:
            # Convert to dictionary
            quote_dict = {
                'id': result[0],
                'content': result[1],
                'book': result[2],
                'author': result[3],
                'entry_date': result[4],
                'value': result[5],
                'last_seen': result[6]
            }
            
            # Calculate new last_seen (current time + 168 hours)
            new_last_seen = current_time + timedelta(hours=168)
            
            # Update last_seen using modify_cell function
            # modify_cell(result[0], 'last_seen', new_last_seen)
            
            return json.dumps(quote_dict, ensure_ascii=False)
        else:
            return json.dumps({'error': 'No quotes available'})
            
    except sqlite3.Error as e:
        return json.dumps({'error': f'Database error: {str(e)}'})
    except Exception as e:
        return json.dumps({'error': f'Unexpected error: {str(e)}'})
    finally:
        if conn:
            conn.close()

