from dataclasses import dataclass


@dataclass
class Book_quotes:
    """
    A class to store book quotes with metadata.
    
    Attributes:
        book (str): The title of the book
        author (str): The author of the book
        content (List[str]): List of quotes from the book
        value (int): Rating value of the book, defaults to 5
    """
    book: str
    author: str
    content: list[str]
    value: int = 5










